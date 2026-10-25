// 8a. Stop double joining: disable the button once the form is submitted.
const joinForm = document.getElementById("join-form");
if (joinForm) {
  const button = joinForm.querySelector("button[type=submit]");
  const originalText = button.textContent;

  joinForm.addEventListener("submit", () => {
    button.disabled = true;
    button.textContent = "Getting your ticket…";
  });

  // If the person taps Back, the browser may keep the disabled button.
  window.addEventListener("pageshow", () => {
    button.disabled = false;
    button.textContent = originalText;
  });
}
