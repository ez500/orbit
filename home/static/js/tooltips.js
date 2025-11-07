/**
 * VerAlign Tooltip System
 * Provides comprehensive tooltip functionality and interactive tutorials
 */

class TooltipManager {
    constructor() {
        this.tooltips = new Map();
        this.activeTooltip = null;
        this.delay = 500; // ms delay before showing tooltip
        this.hideDelay = 100; // ms delay before hiding
        this.timeoutId = null;
        this.hideTimeoutId = null;
    }

    /**
     * Initialize tooltip system
     */
    init() {
        this.initializeTooltips();
        this.setupEventListeners();
        console.log('[Tooltips] Initialized tooltip system');
    }

    /**
     * Find and initialize all tooltip elements
     */
    initializeTooltips() {
        const elements = document.querySelectorAll('[data-tooltip]');
        elements.forEach(element => {
            this.registerTooltip(element);
        });
    }

    /**
     * Register a tooltip for an element
     */
    registerTooltip(element) {
        const tooltipData = {
            text: element.getAttribute('data-tooltip'),
            position: element.getAttribute('data-tooltip-position') || 'top',
            title: element.getAttribute('data-tooltip-title') || null,
            shortcut: element.getAttribute('data-tooltip-shortcut') || null,
            element: element
        };

        this.tooltips.set(element, tooltipData);
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        document.addEventListener('mouseover', (e) => {
            const target = e.target.closest('[data-tooltip]');
            if (target && this.tooltips.has(target)) {
                this.scheduleShow(target);
            }
        });

        document.addEventListener('mouseout', (e) => {
            const target = e.target.closest('[data-tooltip]');
            if (target && this.tooltips.has(target)) {
                this.scheduleHide();
            }
        });

        // Hide on scroll
        document.addEventListener('scroll', () => {
            this.hideAll();
        }, true);
    }

    /**
     * Schedule tooltip display
     */
    scheduleShow(element) {
        // Clear any existing hide timeout
        if (this.hideTimeoutId) {
            clearTimeout(this.hideTimeoutId);
            this.hideTimeoutId = null;
        }

        // Clear any existing show timeout
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }

        // Schedule new tooltip
        this.timeoutId = setTimeout(() => {
            this.show(element);
        }, this.delay);
    }

    /**
     * Schedule tooltip hide
     */
    scheduleHide() {
        // Clear show timeout if exists
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }

        // Schedule hide
        this.hideTimeoutId = setTimeout(() => {
            this.hideAll();
        }, this.hideDelay);
    }

    /**
     * Show tooltip
     */
    show(element) {
        // Hide any existing tooltip
        this.hideAll();

        const data = this.tooltips.get(element);
        if (!data) return;

        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'veralign-tooltip';
        tooltip.setAttribute('data-position', data.position);

        // Build tooltip content
        let content = '';
        if (data.title) {
            content += `<div class="tooltip-title">${data.title}</div>`;
        }
        content += `<div class="tooltip-content">${data.text}</div>`;
        if (data.shortcut) {
            content += `<div class="tooltip-shortcut">${data.shortcut}</div>`;
        }

        tooltip.innerHTML = content;

        // Position tooltip
        element.style.position = 'relative';
        element.appendChild(tooltip);

        // Show tooltip with animation
        requestAnimationFrame(() => {
            tooltip.classList.add('show');
        });

        this.activeTooltip = tooltip;
    }

    /**
     * Hide all tooltips
     */
    hideAll() {
        if (this.activeTooltip) {
            this.activeTooltip.classList.remove('show');
            setTimeout(() => {
                if (this.activeTooltip && this.activeTooltip.parentNode) {
                    this.activeTooltip.parentNode.removeChild(this.activeTooltip);
                }
                this.activeTooltip = null;
            }, 200);
        }
    }

    /**
     * Add a new tooltip programmatically
     */
    addTooltip(element, text, options = {}) {
        element.setAttribute('data-tooltip', text);
        if (options.position) {
            element.setAttribute('data-tooltip-position', options.position);
        }
        if (options.title) {
            element.setAttribute('data-tooltip-title', options.title);
        }
        if (options.shortcut) {
            element.setAttribute('data-tooltip-shortcut', options.shortcut);
        }
        this.registerTooltip(element);
    }

    /**
     * Remove tooltip from element
     */
    removeTooltip(element) {
        this.tooltips.delete(element);
        element.removeAttribute('data-tooltip');
        element.removeAttribute('data-tooltip-position');
        element.removeAttribute('data-tooltip-title');
        element.removeAttribute('data-tooltip-shortcut');
    }
}

/**
 * Interactive Tutorial System
 */
class TutorialManager {
    constructor() {
        this.steps = [];
        this.currentStep = 0;
        this.isActive = false;
        this.overlay = null;
        this.spotlight = null;
        this.tooltipElement = null;
        this.onComplete = null;
        this.storageKey = 'veralign_tutorial_completed';
    }

    /**
     * Define tutorial steps
     */
    defineTutorial(steps) {
        this.steps = steps;
        return this;
    }

    /**
     * Start the tutorial
     */
    start(onComplete = null) {
        if (this.hasCompleted()) {
            console.log('[Tutorial] Already completed');
            return;
        }

        this.onComplete = onComplete;
        this.currentStep = 0;
        this.isActive = true;

        this.createOverlay();
        this.showStep(0);

        console.log('[Tutorial] Started tutorial with', this.steps.length, 'steps');
    }

    /**
     * Force start tutorial (ignore completion status)
     */
    forceStart(onComplete = null) {
        this.onComplete = onComplete;
        this.currentStep = 0;
        this.isActive = true;

        this.createOverlay();
        this.showStep(0);

        console.log('[Tutorial] Force started tutorial');
    }

    /**
     * Create overlay and UI elements
     */
    createOverlay() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tutorial-overlay active';
        document.body.appendChild(this.overlay);

        // Create spotlight
        this.spotlight = document.createElement('div');
        this.spotlight.className = 'tutorial-spotlight';
        document.body.appendChild(this.spotlight);

        // Create close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'tutorial-close active';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.addEventListener('click', () => this.skip());
        document.body.appendChild(closeBtn);
    }

    /**
     * Show a specific step
     */
    showStep(index) {
        if (index < 0 || index >= this.steps.length) {
            this.complete();
            return;
        }

        const step = this.steps[index];
        this.currentStep = index;

        // Find target element
        const targetElement = document.querySelector(step.target);
        if (!targetElement) {
            console.warn('[Tutorial] Target element not found:', step.target);
            this.next();
            return;
        }

        // Position spotlight
        this.positionSpotlight(targetElement);

        // Create/update tooltip
        this.showTooltip(targetElement, step);

        // Scroll to element
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });

        // Add highlight class
        targetElement.classList.add('tooltip-highlight');

        // Optional: Execute callback
        if (step.onShow) {
            step.onShow(targetElement);
        }
    }

    /**
     * Position spotlight on element
     */
    positionSpotlight(element) {
        const rect = element.getBoundingClientRect();
        const padding = 8;

        this.spotlight.style.top = `${rect.top - padding + window.scrollY}px`;
        this.spotlight.style.left = `${rect.left - padding}px`;
        this.spotlight.style.width = `${rect.width + padding * 2}px`;
        this.spotlight.style.height = `${rect.height + padding * 2}px`;
    }

    /**
     * Show tutorial tooltip
     */
    showTooltip(element, step) {
        // Remove existing tooltip
        if (this.tooltipElement) {
            this.tooltipElement.remove();
        }

        // Create tooltip
        this.tooltipElement = document.createElement('div');
        this.tooltipElement.className = 'tutorial-tooltip';

        const stepNum = `${this.currentStep + 1}/${this.steps.length}`;

        this.tooltipElement.innerHTML = `
            <div class="tutorial-header">
                <div class="tutorial-title">${step.title}</div>
                <div class="tutorial-step">${stepNum}</div>
            </div>
            <div class="tutorial-content">${step.content}</div>
            <div class="tutorial-actions">
                <button class="btn-tutorial btn-tutorial-skip">Skip Tutorial</button>
                ${this.currentStep < this.steps.length - 1
                    ? '<button class="btn-tutorial btn-tutorial-next">Next</button>'
                    : '<button class="btn-tutorial btn-tutorial-next">Finish</button>'
                }
            </div>
        `;

        document.body.appendChild(this.tooltipElement);

        // Position tooltip
        this.positionTooltip(element);

        // Show with animation
        requestAnimationFrame(() => {
            this.tooltipElement.classList.add('show');
        });

        // Setup event listeners
        this.tooltipElement.querySelector('.btn-tutorial-skip').addEventListener('click', () => {
            this.skip();
        });

        this.tooltipElement.querySelector('.btn-tutorial-next').addEventListener('click', () => {
            this.next();
        });
    }

    /**
     * Position tutorial tooltip
     */
    positionTooltip(element) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltipElement.getBoundingClientRect();
        const padding = 20;

        // Try to position below element
        let top = rect.bottom + padding + window.scrollY;
        let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);

        // Check if tooltip goes off screen
        if (top + tooltipRect.height > window.innerHeight + window.scrollY) {
            // Position above instead
            top = rect.top - tooltipRect.height - padding + window.scrollY;
        }

        // Ensure left position is within viewport
        if (left < padding) {
            left = padding;
        } else if (left + tooltipRect.width > window.innerWidth - padding) {
            left = window.innerWidth - tooltipRect.width - padding;
        }

        this.tooltipElement.style.top = `${top}px`;
        this.tooltipElement.style.left = `${left}px`;
    }

    /**
     * Go to next step
     */
    next() {
        // Remove highlight from current element
        const currentStep = this.steps[this.currentStep];
        const currentElement = document.querySelector(currentStep.target);
        if (currentElement) {
            currentElement.classList.remove('tooltip-highlight');
        }

        // Show next step
        this.showStep(this.currentStep + 1);
    }

    /**
     * Skip tutorial
     */
    skip() {
        this.cleanup();
        console.log('[Tutorial] Skipped');
    }

    /**
     * Complete tutorial
     */
    complete() {
        this.cleanup();
        this.markCompleted();

        if (this.onComplete) {
            this.onComplete();
        }

        console.log('[Tutorial] Completed');
    }

    /**
     * Cleanup tutorial UI
     */
    cleanup() {
        // Remove highlight from current element
        if (this.currentStep < this.steps.length) {
            const currentStep = this.steps[this.currentStep];
            const currentElement = document.querySelector(currentStep.target);
            if (currentElement) {
                currentElement.classList.remove('tooltip-highlight');
            }
        }

        // Remove UI elements
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }

        if (this.spotlight) {
            this.spotlight.remove();
            this.spotlight = null;
        }

        if (this.tooltipElement) {
            this.tooltipElement.remove();
            this.tooltipElement = null;
        }

        // Remove close button
        const closeBtn = document.querySelector('.tutorial-close');
        if (closeBtn) {
            closeBtn.remove();
        }

        this.isActive = false;
    }

    /**
     * Mark tutorial as completed
     */
    markCompleted() {
        localStorage.setItem(this.storageKey, 'true');
    }

    /**
     * Check if tutorial has been completed
     */
    hasCompleted() {
        return localStorage.getItem(this.storageKey) === 'true';
    }

    /**
     * Reset tutorial completion status
     */
    reset() {
        localStorage.removeItem(this.storageKey);
        console.log('[Tutorial] Reset completion status');
    }
}

// Initialize global instances
const tooltipManager = new TooltipManager();
const tutorialManager = new TutorialManager();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        tooltipManager.init();
    });
} else {
    tooltipManager.init();
}

// Expose globally
window.tooltipManager = tooltipManager;
window.tutorialManager = tutorialManager;

console.log('[Tooltips] Tooltip and tutorial managers loaded');
