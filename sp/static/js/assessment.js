/**
 * Final 10-Question Assessment Manager
 */

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('assessment-form');
  const progressText = document.getElementById('answered-count');
  const progressBar = document.getElementById('assessment-progress');
  const totalQuestions = 10;

  function updateProgress() {
    const radioGroups = new Set();
    const checkedRadios = document.querySelectorAll('#assessment-form input[type="radio"]:checked');
    checkedRadios.forEach(r => radioGroups.add(r.name));

    const count = radioGroups.size;
    if (progressText) progressText.innerText = `${count} of ${totalQuestions} answered`;
    if (progressBar) {
      const pct = (count / totalQuestions) * 100;
      progressBar.style.width = `${pct}%`;
    }
  }

  const inputs = document.querySelectorAll('#assessment-form input[type="radio"]');
  inputs.forEach(input => {
    input.addEventListener('change', updateProgress);
  });

  if (form) {
    form.addEventListener('submit', function (e) {
      const radioGroups = new Set();
      document.querySelectorAll('#assessment-form input[type="radio"]:checked').forEach(r => radioGroups.add(r.name));
      if (radioGroups.size < totalQuestions) {
        if (!confirm(`You have only answered ${radioGroups.size} of ${totalQuestions} questions. Are you sure you want to finalize your submission?`)) {
          e.preventDefault();
        }
      }
    });
  }

  updateProgress();
});

