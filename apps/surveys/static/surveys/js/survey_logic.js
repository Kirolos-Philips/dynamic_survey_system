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
    }

    handleTriggers(triggerId) {
        const targets = this.surveyData.trigger_map[triggerId];
        if (!targets) return;

        targets.forEach(targetId => {
            this.evaluateLogic(targetId);
        });
    }

    evaluateLogic(targetId) {
        const rules = this.surveyData.logic_map[targetId];
        if (!rules) return;

        const wrapper = document.getElementById(`q-wrapper-${targetId}`);
        const question = this.surveyData.questions_map[targetId];

        let shouldShow = true;
        let availableChoices = null;

        rules.forEach(rule => {
            const triggerValue = this.formValues[rule.trigger_question];
            const isMatch = this.checkCondition(triggerValue, rule.operator, rule.value);

            if (rule.action === 'show') {
                shouldShow = isMatch;
            } else if (rule.action === 'include_choices' && isMatch) {
                availableChoices = rule.target_choices;
            }
        });

        if (shouldShow) {
            wrapper.classList.remove('hidden');
        } else {
            wrapper.classList.add('hidden');
        }

        if (availableChoices && (question.type === 'radio' || question.type === 'dropdown')) {
            this.filterChoices(targetId, availableChoices);
        } else {
            this.resetChoices(targetId);
        }
    }

    checkCondition(val1, operator, val2) {
        switch (operator) {
            case 'eq': return val1 == val2;
            case 'neq': return val1 != val2;
            case 'gt': return parseFloat(val1) > parseFloat(val2);
            case 'lt': return parseFloat(val1) < parseFloat(val2);
            case 'contains': return val1 && val1.includes(val2);
            default: return false;
        }
    }

    filterChoices(qId, allowedChoiceIds) {
        const wrapper = document.getElementById(`q-wrapper-${qId}`);
        const radioLabels = wrapper.querySelectorAll('.radio-label');
        radioLabels.forEach(label => {
            const choiceId = parseInt(label.dataset.choiceId);
            if (allowedChoiceIds.includes(choiceId)) {
                label.classList.remove('hidden');
            } else {
                label.classList.add('hidden');
                const input = label.querySelector('input');
                if (input.checked) input.checked = false;
            }
        });

        const select = wrapper.querySelector('select');
        if (select) {
            Array.from(select.options).forEach(option => {
                if (option.value === "") return;
                const choiceId = parseInt(option.dataset.choiceId);
                if (allowedChoiceIds.includes(choiceId)) {
                    option.hidden = false;
                    option.disabled = false;
                } else {
                    option.hidden = true;
                    option.disabled = true;
                    if (select.value == option.value) select.value = "";
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
        const sidebarTitle = document.querySelector('.sidebar-title');
        if (sidebarTitle) {
            const label = this.language === 'ar' ? 'الأقسام' : 'Sections';
            sidebarTitle.innerHTML = `${label} <span style="float: right; opacity: 0.6;">${this.currentStep + 1} / ${this.sections.length}</span>`;
        }

        this.sections.forEach((_, index) => {
            const sidebarItem = document.getElementById(`sidebar-step-${index}`);
            if (sidebarItem) {
                sidebarItem.classList.remove('active', 'completed');
                if (index === this.currentStep) {
                    sidebarItem.classList.add('active');
                } else if (index < this.currentStep) {
                    sidebarItem.classList.add('completed');
                }
            }
        });
    }
}
