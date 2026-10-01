/*
 * AITrailBlazers click-through player.
 *
 * A dependency-free, static slide player for non-technical demo walkthroughs.
 * Open a demo's walkthrough/index.html directly in a browser (no server needed).
 *
 * The page must define `window.WALKTHROUGH` before loading this script:
 *
 *   window.WALKTHROUGH = {
 *     title: "Demo title",
 *     subtitle: "Optional one-liner",
 *     steps: [
 *       {
 *         title: "Step title",
 *         body: "<p>HTML content describing what the audience sees.</p>",
 *         image: "assets/step-1.png",     // optional, relative to index.html
 *         imageAlt: "Screenshot of ...",  // optional
 *         notes: "Presenter talking points" // optional, toggle with the N key
 *       }
 *     ]
 *   };
 *
 * Controls: Next/Back buttons, Left/Right arrow keys, Home/End, N toggles notes.
 * The current step is kept in the URL hash (#step-3) so steps can be deep-linked.
 */
(function () {
  "use strict";

  var data = window.WALKTHROUGH;
  var root = document.getElementById("walkthrough");

  if (!root) {
    return;
  }
  if (!data || !Array.isArray(data.steps) || data.steps.length === 0) {
    root.textContent = "No walkthrough steps defined. Set window.WALKTHROUGH before loading player.js.";
    return;
  }

  var steps = data.steps;
  var current = 0;
  var showNotes = false;

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined) {
      node.textContent = text;
    }
    return node;
  }

  document.title = data.title || document.title;

  var header = el("header", "ct-header");
  header.appendChild(el("h1", "ct-title", data.title || "Walkthrough"));
  if (data.subtitle) {
    header.appendChild(el("p", "ct-subtitle", data.subtitle));
  }

  var progress = el("div", "ct-progress");
  var dots = steps.map(function (step, i) {
    var dot = el("button", "ct-dot");
    dot.type = "button";
    dot.setAttribute("aria-label", "Go to step " + (i + 1) + ": " + (step.title || ""));
    dot.addEventListener("click", function () {
      go(i);
    });
    progress.appendChild(dot);
    return dot;
  });

  var stage = el("main", "ct-stage");
  stage.setAttribute("aria-live", "polite");
  var counter = el("p", "ct-counter");
  var stepTitle = el("h2", "ct-step-title");
  var figure = el("figure", "ct-figure");
  var image = el("img", "ct-image");
  var caption = el("figcaption", "ct-caption");
  figure.appendChild(image);
  figure.appendChild(caption);
  var body = el("div", "ct-body");
  var notes = el("aside", "ct-notes");

  stage.appendChild(counter);
  stage.appendChild(stepTitle);
  stage.appendChild(figure);
  stage.appendChild(body);
  stage.appendChild(notes);

  var nav = el("nav", "ct-nav");
  var back = el("button", "ct-btn ct-back", "\u2190 Back");
  back.type = "button";
  var notesBtn = el("button", "ct-btn ct-notes-toggle", "Presenter notes");
  notesBtn.type = "button";
  var next = el("button", "ct-btn ct-next", "Next \u2192");
  next.type = "button";
  nav.appendChild(back);
  nav.appendChild(notesBtn);
  nav.appendChild(next);

  root.appendChild(header);
  root.appendChild(progress);
  root.appendChild(stage);
  root.appendChild(nav);

  back.addEventListener("click", function () {
    go(current - 1);
  });
  next.addEventListener("click", function () {
    go(current + 1);
  });
  notesBtn.addEventListener("click", toggleNotes);

  document.addEventListener("keydown", function (event) {
    if (event.target && /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) {
      return;
    }
    switch (event.key) {
      case "ArrowRight":
      case "PageDown":
        go(current + 1);
        break;
      case "ArrowLeft":
      case "PageUp":
        go(current - 1);
        break;
      case "Home":
        go(0);
        break;
      case "End":
        go(steps.length - 1);
        break;
      case "n":
      case "N":
        toggleNotes();
        break;
      default:
        return;
    }
    event.preventDefault();
  });

  window.addEventListener("hashchange", function () {
    var fromHash = indexFromHash();
    if (fromHash !== current) {
      render(fromHash);
    }
  });

  function toggleNotes() {
    showNotes = !showNotes;
    render(current);
  }

  function indexFromHash() {
    var match = /^#step-(\d+)$/.exec(window.location.hash);
    if (!match) {
      return 0;
    }
    return clamp(parseInt(match[1], 10) - 1);
  }

  function clamp(i) {
    return Math.max(0, Math.min(steps.length - 1, i));
  }

  function go(i) {
    i = clamp(i);
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", "#step-" + (i + 1));
    }
    render(i);
  }

  function render(i) {
    current = clamp(i);
    var step = steps[current];

    counter.textContent = "Step " + (current + 1) + " of " + steps.length;
    stepTitle.textContent = step.title || "";
    // Step bodies are authored by demo maintainers in this repository.
    body.innerHTML = step.body || "";

    if (step.image) {
      image.src = step.image;
      image.alt = step.imageAlt || step.title || "";
      caption.textContent = step.imageAlt || "";
      figure.hidden = false;
    } else {
      image.removeAttribute("src");
      figure.hidden = true;
    }

    var hasNotes = Boolean(step.notes);
    notes.textContent = step.notes || "";
    notes.hidden = !(showNotes && hasNotes);
    notesBtn.hidden = !hasNotes;
    notesBtn.setAttribute("aria-pressed", String(showNotes));

    back.disabled = current === 0;
    next.disabled = current === steps.length - 1;

    dots.forEach(function (dot, d) {
      dot.classList.toggle("ct-dot-active", d === current);
      dot.classList.toggle("ct-dot-done", d < current);
      if (d === current) {
        dot.setAttribute("aria-current", "step");
      } else {
        dot.removeAttribute("aria-current");
      }
    });
  }

  render(indexFromHash());
})();
