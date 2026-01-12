class SurveyRenderer {
    constructor(containerId, surveyId, language) {
        this.container = document.getElementById(containerId);
        this.surveyId = surveyId;
        this.language = language;
        this.surveyData = null;
        this.formValues = {};
        this.currentStep = 0;
        this.sections = [];
    }

    async init() {
        try {
            const response = await fetch(`/api/surveys/${this.surveyId}/data/`, {
                headers: {
                    'Accept-Language': this.language
                }
            });
            this.surveyData = await response.json();
            this.prepareSections();
            this.render();
            this.applyInitialLogic();
            this.updateStepVisibility();
        } catch (error) {
            console.error('Error loading survey:', error);
            this.container.innerHTML = '<div class="error-msg">Failed to load survey.</div>';
        }
    }

    prepareSections() {
        const { questions_map } = this.surveyData;
        const sectionMap = {};
        Object.values(questions_map).forEach(q => {
            if (!sectionMap[q.section]) {
                sectionMap[q.section] = [];
            }
            sectionMap[q.section].push(q);
        });
        this.sections = Object.keys(sectionMap).map(title => ({
            title,
            questions: sectionMap[title]
        }));
    }

    render() {
        const { title, description } = this.surveyData;

        // Render Sidebar Steps
        this.renderSidebar();

        let html = `
            <div class="survey-header">
                <h1>${title}</h1>
                <p class="description">${description}</p>
            </div>
            
            <div class="progress-bar-container">
                <div class="progress-bar-fill" id="progress-fill"></div>
            </div>

            <form id="survey-form">
                <div id="steps-container">
        `;

        this.sections.forEach((section, index) => {
            html += `
                <div class="survey-section" data-step="${index}" style="display: ${index === 0 ? 'block' : 'none'}">
                    <h2 class="section-title">${section.title}</h2>
                    <div class="questions-container">
                        ${section.questions.map(q => this.renderQuestion(q)).join('')}
                    </div>
                </div>
            `;
        });

        html += `
                </div>
                <div class="form-footer">
                    <button type="button" id="prev-btn" class="nav-btn prev" style="display: none">Back</button>
                    <button type="button" id="next-btn" class="nav-btn next">Next</button>
                    <button type="submit" id="submit-btn" class="submit-btn" style="display: none">Submit Survey</button>
                </div>
            </form>
        `;

        this.container.innerHTML = html;
        this.attachEventListeners();
        this.updateProgress();
    }

    renderQuestion(q) {
        let inputHtml = '';
        const name = `question_${q.id}`;

        if (q.type === 'radio') {
            inputHtml = q.choices.map(choice => `
                <label class="radio-label" data-choice-id="${choice.id}">
                    <input type="radio" name="${name}" value="${choice.value}" data-question-id="${q.id}" data-choice-id="${choice.id}">
                    <span class="radio-custom"></span>
                    <span class="choice-text">${choice.label}</span>
                </label>
            `).join('');
        } else if (q.type === 'dropdown') {
            inputHtml = `
                <div class="select-wrapper">
                    <select name="${name}" data-question-id="${q.id}" class="survey-select">
                        <option value="" disabled selected>Select an option</option>
                        ${q.choices.map(choice => `
                            <option value="${choice.value}" data-choice-id="${choice.id}">${choice.label}</option>
                        `).join('')}
                    </select>
                </div>
            `;
        } else if (q.type === 'number') {
            inputHtml = `
                <input type="number" name="${name}" data-question-id="${q.id}" class="survey-input" placeholder="Enter a number">
            `;
        }

        return `
            <div class="question-wrapper" id="q-wrapper-${q.id}" data-question-id="${q.id}">
                <label class="question-text">${q.text}</label>
                <div class="input-container">
                    ${inputHtml}
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const form = document.getElementById('survey-form');
        form.addEventListener('change', (e) => {
            const target = e.target;
            const qId = target.dataset.questionId;
            if (qId) {
                this.updateValue(qId, target.value);
                this.handleTriggers(qId);
            }
        });

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Form Submitted:', this.formValues);
            alert('Survey submitted! Check console for data.');
        });

        document.getElementById('next-btn').addEventListener('click', () => this.nextStep());
        document.getElementById('prev-btn').addEventListener('click', () => this.prevStep());

        const stepsList = document.getElementById('steps-list');
        if (stepsList) {
            stepsList.addEventListener('click', (e) => {
                const stepItem = e.target.closest('.step-item');
                if (stepItem) {
                    const stepIndex = parseInt(stepItem.dataset.step);
                    this.goToStep(stepIndex);
                }
            });
        }
    }

    goToStep(index) {
        if (index >= 0 && index < this.sections.length) {
            this.currentStep = index;
            this.updateStepVisibility();
        }
    }

    nextStep() {
        if (this.currentStep < this.sections.length - 1) {
            this.currentStep++;
            this.updateStepVisibility();
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateStepVisibility();
        }
    }

    updateStepVisibility() {
        const steps = document.querySelectorAll('.survey-section');
        steps.forEach((step, index) => {
            step.style.display = index === this.currentStep ? 'block' : 'none';
        });


        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const submitBtn = document.getElementById('submit-btn');

        prevBtn.style.display = this.currentStep === 0 ? 'none' : 'block';

        if (this.currentStep === this.sections.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'block';
        } else {
            nextBtn.style.display = 'block';
            submitBtn.style.display = 'none';
        }

        this.updateProgress();
        this.updateSidebarState();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    updateProgress() {
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            const progress = ((this.currentStep + 1) / this.sections.length) * 100;
            progressFill.style.width = `${progress}%`;
        }
    }

    updateValue(qId, value) {
        this.formValues[qId] = value;
        this.updateSidebarState();
    }

    handleTriggers(triggerId) {
        const targets = this.surveyData.trigger_map[triggerId];
        if (!targets) return;

        targets.forEach(targetId => {
            this.evaluateLogic(targetId);
        });
    }

    evaluateLogic(targetId) {
        const targetIdStr = String(targetId);
        const rules = this.surveyData.logic_map[targetIdStr];
        if (!rules) return;

        const question = this.surveyData.questions_map[targetIdStr];
        const wrapper = document.getElementById(`q-wrapper-${targetIdStr}`);
        if (!question || !wrapper) return;

        // Visibility State
        const hasShowRules = rules.some(r => r.action === 'show');
        let showMatched = false;
        let hideMatched = false;

        // Choice Filtering State
        let allowedChoiceIds = null;

        rules.forEach(rule => {
            const triggerValue = this.formValues[String(rule.trigger_question)];
            const isMatch = this.checkCondition(triggerValue, rule.operator, rule.value);

            if (isMatch) {
                switch (rule.action) {
                    case 'show':
                        showMatched = true;
                        break;
                    case 'hide':
                        hideMatched = true;
                        break;
                    case 'limit_choices':
                    case 'include_choices':
                        if (allowedChoiceIds === null) allowedChoiceIds = new Set();
                        (rule.target_choices || []).forEach(id => allowedChoiceIds.add(Number(id)));
                        break;
                    case 'exclude_choices':
                        if (allowedChoiceIds === null) {
                            allowedChoiceIds = new Set(question.choices.map(c => Number(c.id)));
                        }
                        (rule.target_choices || []).forEach(id => allowedChoiceIds.delete(Number(id)));
                        break;
                }
            }
        });

        // Determine Visibility
        const shouldShow = hasShowRules ? (showMatched && !hideMatched) : !hideMatched;
        wrapper.style.display = shouldShow ? 'block' : 'none';
        wrapper.classList.toggle('hidden', !shouldShow);

        // Determine Final Choices Array
        if (question.type === 'radio' || question.type === 'dropdown') {
            if (allowedChoiceIds !== null) {
                const choiceList = Array.from(allowedChoiceIds);
                console.log(`[Logic] Question ${targetIdStr}: Filtering to choices`, choiceList);
                this.filterChoices(targetIdStr, choiceList);
            } else {
                this.resetChoices(targetIdStr);
            }
        }
        this.updateSidebarState();
    }

    checkCondition(val1, operator, val2) {
        if (val1 === undefined || val1 === null) return false;

        const v1 = String(val1).toLowerCase().trim();
        const v2 = String(val2).toLowerCase().trim();

        switch (operator) {
            case 'eq': return v1 == v2;
            case 'neq': return v1 != v2;
            case 'gt': return parseFloat(v1) > parseFloat(v2);
            case 'lt': return parseFloat(v1) < parseFloat(v2);
            case 'contains': return v1.includes(v2);
            default: return false;
        }
    }

    filterChoices(qId, allowedChoiceIds) {
        const wrapper = document.getElementById(`q-wrapper-${qId}`);
        const allowed = allowedChoiceIds.map(id => Number(id));

        // Filter Radio Buttons
        const radioLabels = wrapper.querySelectorAll('.radio-label');
        radioLabels.forEach(label => {
            const choiceId = Number(label.dataset.choiceId);
            const isAllowed = allowed.includes(choiceId);
            label.style.display = isAllowed ? 'flex' : 'none';
            label.classList.toggle('hidden', !isAllowed);

            const input = label.querySelector('input');
            if (!isAllowed && input && input.checked) {
                input.checked = false;
                this.updateValue(qId, null);
            }
        });

        // Filter Dropdown Options
        const select = wrapper.querySelector('select');
        if (select) {
            Array.from(select.options).forEach(option => {
                if (option.value === "") return;
                const choiceId = Number(option.dataset.choiceId);
                const isAllowed = allowed.includes(choiceId);

                option.hidden = !isAllowed;
                option.disabled = !isAllowed;
                option.style.display = isAllowed ? 'block' : 'none';

                if (!isAllowed && select.value === option.value) {
                    select.value = "";
                    this.updateValue(qId, null);
                }
            });
        }
    }

    resetChoices(qId) {
        const wrapper = document.getElementById(`q-wrapper-${qId}`);
        if (!wrapper) return;
        const radioLabels = wrapper.querySelectorAll('.radio-label');
        radioLabels.forEach(label => label.classList.remove('hidden'));

        const select = wrapper.querySelector('select');
        if (select) {
            Array.from(select.options).forEach(option => {
                option.hidden = false;
                option.disabled = false;
            });
        }
    }

    applyInitialLogic() {
        Object.keys(this.surveyData.logic_map).forEach(targetId => {
            this.evaluateLogic(targetId);
        });
    }

    renderSidebar() {
        const stepsList = document.getElementById('steps-list');
        if (!stepsList) return;

        stepsList.innerHTML = this.sections.map((section, index) => `
            <div class="step-item" id="sidebar-step-${index}" data-step="${index}">
                <div class="step-number">
                    <span class="step-label-num">${index + 1}</span>
                </div>
                <div class="step-label">${section.title}</div>
            </div>
        `).join('');
        this.updateSidebarState();
    }

    updateSidebarState() {
        if (!this.sections.length) return;

        const sidebarTitle = document.querySelector('.sidebar-title');
        if (sidebarTitle) {
            const label = this.language === 'ar' ? 'الأقسام' : 'Sections';
            sidebarTitle.innerHTML = `${label} <span style="float: right; opacity: 0.6;">${this.currentStep + 1} / ${this.sections.length}</span>`;
        }

        this.sections.forEach((section, index) => {
            const sidebarItem = document.getElementById(`sidebar-step-${index}`);
            if (sidebarItem) {
                sidebarItem.classList.toggle('active', index === this.currentStep);

                // Logic for "completed": Check if all VISIBLE questions have values
                const isCompleted = section.questions.every(q => {
                    const wrapper = document.getElementById(`q-wrapper-${q.id}`);
                    const isHidden = wrapper && (wrapper.style.display === 'none' || wrapper.classList.contains('hidden'));
                    if (isHidden) return true;

                    const val = this.formValues[q.id];
                    return val !== undefined && val !== null && val !== '';
                });

                sidebarItem.classList.toggle('completed', isCompleted);
            }
        });
    }
}
