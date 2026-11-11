/**
 * Timed Alert Questions Client Manager
 * Checks for task-relevant alert questions, displays modal with 5-minute timer,
 * and submits student responses or logs timeouts.
 */

window.AlertSystem = {
  sessionCode: null,
  taskNumber: 1,
  activeAlertId: null,
  timerInterval: null,
  remainingSeconds: 300,
  hasTriggeredForTask: false,

  init: function (sessionCode, taskNumber) {
    this.sessionCode = sessionCode;
    this.taskNumber = taskNumber;
    this.hasTriggeredForTask = false;

    // Trigger alert query after 30 seconds into the task
    setTimeout(() => {
      this.checkAndDisplayAlert();
    }, 30000);
  },

  checkAndDisplayAlert: function () {
    if (this.hasTriggeredForTask || !this.sessionCode) return;

    fetch(`/lab/${this.sessionCode}/alert/get?task=${this.taskNumber}`)
      .then(res => res.json())
      .then(data => {
        if (data.has_alert) {
          this.hasTriggeredForTask = true;
          this.showModal(data);
        }
      })
      .catch(err => console.warn("Alert poll failed:", err));
  },

  showModal: function (alertData) {
    this.activeAlertId = alertData.alert_id;
    this.remainingSeconds = alertData.timeout_seconds || 300;

    let backdrop = document.getElementById('alert-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.id = 'alert-backdrop';
      backdrop.className = 'alert-popup-backdrop';
      document.body.appendChild(backdrop);
    }

    backdrop.innerHTML = `
      <div class="alert-popup-card">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="badge bg-primary">Concept Check (${alertData.task_number})</span>
          <span class="text-danger fw-bold" id="alert-timer-display">05:00</span>
        </div>
        <div class="timer-progress mb-3">
          <div class="timer-bar" id="alert-progress-bar" style="width: 100%;"></div>
        </div>
        <h6 class="fw-bold text-dark mb-3">${alertData.question}</h6>
        <div class="list-group mb-3">
          ${Object.entries(alertData.options).map(([optKey, optVal]) => `
            <label class="list-group-item list-group-item-action d-flex align-items-center gap-2 cursor-pointer">
              <input class="form-check-input flex-shrink-0" type="radio" name="alert_opt" value="${optKey}">
              <span><strong>${optKey}:</strong> ${optVal}</span>
            </label>
          `).join('')}
        </div>
        <div class="d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary btn-sm" id="alert-dismiss-btn">Dismiss</button>
          <button type="button" class="btn btn-primary-custom btn-sm" id="alert-submit-btn">Submit Answer</button>
        </div>
      </div>
    `;

    backdrop.style.display = 'flex';

    // Timer countdown
    const timerDisplay = document.getElementById('alert-timer-display');
    const progressBar = document.getElementById('alert-progress-bar');
    const totalTime = this.remainingSeconds;

    this.timerInterval = setInterval(() => {
      this.remainingSeconds--;
      const mins = String(Math.floor(this.remainingSeconds / 60)).padStart(2, '0');
      const secs = String(this.remainingSeconds % 60).padStart(2, '0');
      if (timerDisplay) timerDisplay.innerText = `${mins}:${secs}`;
      
      const pct = (this.remainingSeconds / totalTime) * 100;
      if (progressBar) progressBar.style.width = `${pct}%`;

      if (this.remainingSeconds <= 0) {
        clearInterval(this.timerInterval);
        this.submitResponse('TIMEOUT');
      }
    }, 1000);

    document.getElementById('alert-submit-btn').addEventListener('click', () => {
      const selected = document.querySelector('input[name="alert_opt"]:checked');
      if (!selected) {
        alert("Please select an option before submitting.");
        return;
      }
      this.submitResponse(selected.value);
    });

    document.getElementById('alert-dismiss-btn').addEventListener('click', () => {
      this.submitResponse('TIMEOUT');
    });
  },

  submitResponse: function (chosenAnswer) {
    if (this.timerInterval) clearInterval(this.timerInterval);

    fetch(`/lab/${this.sessionCode}/alert/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        alert_id: this.activeAlertId,
        answer: chosenAnswer
      })
    })
      .then(res => res.json())
      .then(() => {
        const backdrop = document.getElementById('alert-backdrop');
        if (backdrop) backdrop.style.display = 'none';
      })
      .catch(() => {
        const backdrop = document.getElementById('alert-backdrop');
        if (backdrop) backdrop.style.display = 'none';
      });
  }
};

