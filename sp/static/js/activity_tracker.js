/**
 * Client-Side Programming Activity Tracker
 * Tracks typing keystrokes, editor edits, idle intervals, and tab focus.
 */

window.ActivityTracker = {
  sessionCode: null,
  taskNumber: 1,
  keystrokesCount: 0,
  editsCount: 0,
  timeSpentSeconds: 0,
  lastActivityTimestamp: Date.now(),
  idleThresholdSeconds: 25,
  isCurrentlyIdle: false,
  timerInterval: null,
  syncInterval: null,

  init: function (sessionCode, taskNumber) {
    this.sessionCode = sessionCode;
    this.taskNumber = taskNumber;
    this.lastActivityTimestamp = Date.now();

    const editor = document.getElementById('code-editor');
    if (editor) {
      editor.addEventListener('keydown', (e) => this.onKeyDown(e));
      editor.addEventListener('input', (e) => this.onInput(e));
      editor.addEventListener('paste', (e) => this.onPaste(e));
    }

    // Window activity listeners
    window.addEventListener('mousemove', () => this.registerInteraction());
    window.addEventListener('click', () => this.registerInteraction());
    window.addEventListener('blur', () => this.onTabChange(false));
    window.addEventListener('focus', () => this.onTabChange(true));

    // Start 1-second activity clock
    this.timerInterval = setInterval(() => {
      this.timeSpentSeconds++;
      const timeDisplay = document.getElementById('task-timer');
      if (timeDisplay) {
        const mins = String(Math.floor(this.timeSpentSeconds / 60)).padStart(2, '0');
        const secs = String(this.timeSpentSeconds % 60).padStart(2, '0');
        timeDisplay.innerText = `${mins}:${secs}`;
      }

      // Check for idle condition
      const secondsSinceLastAction = (Date.now() - this.lastActivityTimestamp) / 1000;
      if (secondsSinceLastAction >= this.idleThresholdSeconds && !this.isCurrentlyIdle) {
        this.isCurrentlyIdle = true;
        this.sendEvent('idle', { duration: Math.floor(secondsSinceLastAction) });
      }
    }, 1000);

    // Periodic telemetry heartbeat every 30 seconds
    this.syncInterval = setInterval(() => {
      this.sendEvent('heartbeat', {
        keystrokes: this.keystrokesCount,
        edits: this.editsCount,
        time_spent: this.timeSpentSeconds
      });
    }, 30000);
  },

  registerInteraction: function () {
    if (this.isCurrentlyIdle) {
      this.isCurrentlyIdle = false;
      this.sendEvent('active_resume', {});
    }
    this.lastActivityTimestamp = Date.now();
  },

  onKeyDown: function (e) {
    this.registerInteraction();
    this.keystrokesCount++;
    const badge = document.getElementById('keystrokes-badge');
    if (badge) badge.innerText = `${this.keystrokesCount} keys`;
  },

  onInput: function (e) {
    this.registerInteraction();
    this.editsCount++;
    const badge = document.getElementById('edits-badge');
    if (badge) badge.innerText = `${this.editsCount} edits`;
  },

  onPaste: function (e) {
    this.sendEvent('copy_paste', { length: e.clipboardData ? e.clipboardData.getData('text').length : 0 });
  },

  onTabChange: function (isFocused) {
    this.sendEvent('tab_switch', { focused: isFocused });
  },

  sendEvent: function (eventType, details) {
    if (!this.sessionCode) return;
    fetch(`/lab/${this.sessionCode}/telemetry/event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        task_number: this.taskNumber,
        event_type: eventType,
        details: details
      })
    }).catch(() => {});
  },

  getStats: function () {
    return {
      keystrokes: this.keystrokesCount,
      edits: this.editsCount,
      timeSpent: this.timeSpentSeconds
    };
  }
};

