/* Smart Music Tagger — GUI client logic.
 *
 * Collects the config form, POSTs to /api/run to start a background job, then
 * subscribes to /api/stream/<job_id> via Server-Sent Events to render live
 * per-file progress. A late-arriving tab still sees the full history because
 * the server buffers events per job.
 */
(function () {
  "use strict";

  // ─── DOM references ───
  const form = document.getElementById("run-form");
  const runBtn = document.getElementById("run-btn");
  const runAgainBtn = document.getElementById("run-again-btn");
  const statusBadge = document.getElementById("status-badge");

  const configCard = document.getElementById("config-card");
  const progressCard = document.getElementById("progress-card");
  const summaryCard = document.getElementById("summary-card");
  const errorBanner = document.getElementById("error-banner");

  const statFiles = document.getElementById("stat-files");
  const statSuccess = document.getElementById("stat-success");
  const statFailed = document.getElementById("stat-failed");
  const progressFill = document.getElementById("progress-fill");
  const resultList = document.getElementById("result-list");
  const summaryBody = document.getElementById("summary-body");

  let successCount = 0;
  let failedCount = 0;
  let total = 0;
  let currentEs = null;

  // ─── Helpers ───
  function setBadge(text, cls) {
    statusBadge.textContent = text;
    statusBadge.className = "badge " + (cls || "");
  }

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.remove("hidden");
  }
  function clearError() { errorBanner.classList.add("hidden"); }

  function resetProgress(fileCount) {
    successCount = 0;
    failedCount = 0;
    total = fileCount || 0;
    resultList.innerHTML = "";
    statFiles.textContent = "0 / " + (total || 0);
    statSuccess.textContent = "0";
    statFailed.textContent = "0";
    progressFill.style.width = "0%";
    summaryCard.classList.add("hidden");
    summaryBody.innerHTML = "";
    clearError();
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  function metadataTags(meta) {
    if (!meta) return "";
    const parts = [];
    const artists = (meta.artists || []).join(", ");
    if (artists) parts.push("Artist: " + artists);
    if (meta.album) parts.push("Album: " + meta.album);
    if (meta.genre) parts.push("Genre: " + meta.genre);
    if (meta.release_year) parts.push("Year: " + meta.release_year);
    return parts.map(function (p) { return '<span class="tag">' + esc(p) + "</span>"; }).join("");
  }

  function renderProgress(ev) {
    const li = document.createElement("li");
    li.className = "result-item " + (ev.success ? "ok" : "fail");

    let html = '<div class="result-index">[' + ev.index + " / " + ev.total + "]</div>";
    html += '<div class="result-name">' + esc(ev.filename) + "</div>";

    if (ev.success) {
      successCount++;
      if (ev.new_filename && ev.new_filename !== ev.filename) {
        html += '<div class="result-arrow">↓ renamed to</div>';
        html += '<div class="result-new">' + esc(ev.new_filename) + "</div>";
      }
      const tags = metadataTags(ev.metadata);
      if (tags) html += '<div class="result-meta">' + tags + "</div>";
    } else {
      failedCount++;
      const errs = (ev.errors || []).map(function (e) { return esc(e); }).join("<br>");
      if (errs) html += '<div class="result-errors">' + errs + "</div>";
    }
    li.innerHTML = html;
    resultList.appendChild(li);

    const done = ev.index;
    statFiles.textContent = done + " / " + ev.total;
    statSuccess.textContent = String(successCount);
    statFailed.textContent = String(failedCount);
    progressFill.style.width = (ev.total ? (done / ev.total) * 100 : 0) + "%";
  }

  function renderSummary(data) {
    const s = data.summary || {};
    const rate = s.total ? ((s.successful / s.total) * 100).toFixed(1) : "0.0";
    let html = '<div class="summary-grid">';
    html += statBlock("Total", s.total);
    html += statBlock("Successful", s.successful, "ok");
    html += statBlock("Failed", s.failed, "err");
    html += statBlock("Success Rate", rate + "%");
    html += "</div>";
    if (s.log_file) {
      html += '<p class="summary-log">Log file: ' + esc(s.log_file) + "</p>";
    }
    summaryBody.innerHTML = html;
    summaryCard.classList.remove("hidden");
    runAgainBtn.classList.remove("hidden");
  }

  function statBlock(label, value, cls) {
    return '<div class="stat"><span class="stat-label">' + esc(label) +
      '</span><span class="stat-value ' + (cls || "") + '">' + esc(value) + "</span></div>";
  }

  // ─── SSE subscription ───
  function subscribe(jobId) {
    if (currentEs) { currentEs.close(); }
    const es = new EventSource("/api/stream/" + jobId);
    currentEs = es;

    es.addEventListener("started", function (e) {
      const data = JSON.parse(e.data);
      resetProgress(data.file_count);
    });

    es.addEventListener("progress", function (e) {
      renderProgress(JSON.parse(e.data));
    });

    es.addEventListener("done", function (e) {
      const data = JSON.parse(e.data);
      setBadge("Done", "done");
      renderSummary(data);
      runBtn.disabled = false;
      es.close();
      currentEs = null;
    });

    es.addEventListener("failed", function (e) {
      const data = JSON.parse(e.data);
      setBadge("Failed", "failed");
      showError(data.error || "Processing failed.");
      runBtn.disabled = false;
      es.close();
      currentEs = null;
    });

    es.onerror = function () {
      // The server closes the stream on completion; only surface an error if
      // we never reached a terminal event.
      if (statusBadge.textContent !== "Done" && statusBadge.textContent !== "Failed") {
        setBadge("Disconnected", "failed");
        showError("Lost connection to the server.");
      }
      es.close();
      currentEs = null;
    };
  }

  // ─── Form submission ───
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearError();

    const payload = {
      groq_api_key: document.getElementById("groq_api_key").value,
      groq_api_url: document.getElementById("groq_api_url").value,
      groq_model: document.getElementById("groq_model").value,
      groq_request_delay_seconds: document.getElementById("groq_request_delay_seconds").value,
      music_directory: document.getElementById("music_directory").value,
    };

    runBtn.disabled = true;
    setBadge("Starting…", "running");
    progressCard.classList.remove("hidden");
    resetProgress(0);

    fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (r) {
        if (!r.ok || !r.body.job_id) {
          throw new Error(r.body.error || "Failed to start job.");
        }
        setBadge("Running", "running");
        subscribe(r.body.job_id);
      })
      .catch(function (err) {
        setBadge("Error", "failed");
        showError(err.message);
        runBtn.disabled = false;
      });
  });

  runAgainBtn.addEventListener("click", function () {
    progressCard.classList.add("hidden");
    summaryCard.classList.add("hidden");
    runAgainBtn.classList.add("hidden");
    configCard.scrollIntoView({ behavior: "smooth" });
    setBadge("Idle", "");
  });
})();
