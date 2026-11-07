
const prompt = document.getElementById("prompt");
const counter = document.getElementById("counter");
const generate = document.getElementById("generate");
const status = document.getElementById("status");
const preview = document.getElementById("preview");

let selectedRatio = "9:16";
let selectedDuration = "8";

prompt.addEventListener("input", () => {
  counter.textContent = `${prompt.value.length} / 1500`;
});

function setupChoices(groupId, callback) {
  const group = document.getElementById(groupId);

  group.querySelectorAll(".choice").forEach(button => {
    button.addEventListener("click", () => {
      group.querySelectorAll(".choice").forEach(item => {
        item.classList.remove("selected");
      });

      button.classList.add("selected");
      callback(button.dataset.value);
    });
  });
}

setupChoices("ratio", value => {
  selectedRatio = value;
});

setupChoices("duration", value => {
  selectedDuration = value;
});

generate.addEventListener("click", () => {
  const text = prompt.value.trim();

  if (!text) {
    status.textContent = "Please describe your video first.";
    prompt.focus();
    return;
  }

  const style = document.getElementById("style").value;

  status.textContent = "Your video settings are ready!";

  preview.innerHTML = `
    <div class="preview-icon">✦</div>
    <strong>Video project created</strong>
    <p>${escapeText(text)}</p>
    <p>Style: ${style}</p>
    <p>Format: ${selectedRatio}</p>
    <p>Duration: ${selectedDuration} seconds</p>
    <p>Waiting for Veo connection.</p>
  `;

  generate.textContent = "✦ Preview Created";
});

function escapeText(value) {
  const element = document.createElement("div");
  element.textContent = value;
  return element.innerHTML;
}
