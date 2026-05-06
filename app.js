const data = window.HAEDONG_DATA;
const summaries = window.HAEDONG_SUMMARIES || {};

const state = {
  volumeIndex: 0,
  chapterId: null,
  query: "",
};

const volumeTabs = document.querySelector("#volumeTabs");
const chapterList = document.querySelector("#chapterList");
const summary = document.querySelector("#summary");
const chapter = document.querySelector("#chapter");
const notesList = document.querySelector("#notesList");
const searchInput = document.querySelector("#searchInput");
const toggleNotes = document.querySelector("#toggleNotes");

function stripTags(value) {
  const node = document.createElement("div");
  node.innerHTML = value || "";
  return node.textContent || "";
}

function normalize(value) {
  return (value || "").toLocaleLowerCase("ko-KR");
}

function activeVolume() {
  return data.volumes[state.volumeIndex];
}

function allChapterText(chapterData) {
  const chapterSummary = summaries[chapterData.id];
  return [
    chapterData.title,
    chapterData.rawTitle,
    chapterSummary?.role || "",
    chapterSummary?.easy || "",
    ...(chapterSummary?.points || []),
    ...chapterData.paragraphs.map((paragraph) => stripTags(paragraph.html)),
    ...chapterData.notes.map((note) => `${note.type} ${stripTags(note.html)}`),
  ].join(" ");
}

function renderSummaryCard(chapterData) {
  const chapterSummary = summaries[chapterData.id];
  if (!chapterSummary) {
    return `
      <section class="translation-summary muted-summary">
        <h3>알기 쉬운 요약</h3>
        <p>이 항목은 고승 개인의 전기라기보다 머리말이나 목차 성격이 강해 별도 인물 요약을 두지 않았습니다.</p>
      </section>
    `;
  }

  const points = chapterSummary.points
    .map((point) => `<li>${highlight(point, state.query)}</li>`)
    .join("");

  return `
    <section class="translation-summary">
      <div class="summary-label">번역본 쉬운 요약</div>
      <h3>${highlight(chapterSummary.role, state.query)}</h3>
      <p class="summary-easy">${highlight(chapterSummary.easy, state.query)}</p>
      <ul>${points}</ul>
    </section>
  `;
}

function filteredChapters() {
  const query = normalize(state.query);
  return activeVolume().chapters.filter((chapterData) => {
    if (!query) return true;
    return normalize(allChapterText(chapterData)).includes(query);
  });
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlight(html, query) {
  if (!query) return html;
  const pattern = new RegExp(`(${escapeRegExp(query)})`, "gi");
  const wrapper = document.createElement("div");
  wrapper.innerHTML = html;

  const walker = document.createTreeWalker(wrapper, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) {
    textNodes.push(walker.currentNode);
  }

  textNodes.forEach((node) => {
    const text = node.nodeValue;
    if (!pattern.test(text)) return;
    pattern.lastIndex = 0;
    const fragment = document.createDocumentFragment();
    let lastIndex = 0;
    let match = pattern.exec(text);
    while (match) {
      if (match.index > lastIndex) {
        fragment.append(document.createTextNode(text.slice(lastIndex, match.index)));
      }
      const mark = document.createElement("mark");
      mark.textContent = match[0];
      fragment.append(mark);
      lastIndex = match.index + match[0].length;
      match = pattern.exec(text);
    }
    if (lastIndex < text.length) {
      fragment.append(document.createTextNode(text.slice(lastIndex)));
    }
    node.replaceWith(fragment);
  });

  return wrapper.innerHTML;
}

function renderSummary() {
  const volume = activeVolume();
  const stats = data.stats;
  summary.innerHTML = `
    <div class="summary-main">
      <h2>${volume.series || volume.title}</h2>
      <p>${volume.coverage}</p>
    </div>
    <div class="stat"><b>${stats.volumes}</b><span>권</span></div>
    <div class="stat"><b>${stats.chapters}</b><span>항목</span></div>
    <div class="stat"><b>${stats.paragraphs}</b><span>문단</span></div>
    <div class="stat"><b>${stats.notes}</b><span>주석</span></div>
  `;
}

function renderTabs() {
  volumeTabs.innerHTML = data.volumes
    .map((volume, index) => {
      const active = index === state.volumeIndex ? " active" : "";
      return `<button class="tab${active}" type="button" data-volume="${index}">${volume.series}</button>`;
    })
    .join("");
}

function renderChapterList() {
  const chapters = filteredChapters();
  if (!chapters.some((item) => item.id === state.chapterId)) {
    state.chapterId = chapters[0]?.id || activeVolume().chapters[0]?.id || null;
  }

  chapterList.innerHTML =
    chapters
      .map((chapterData) => {
        const active = chapterData.id === state.chapterId ? " active" : "";
        const hasSummary = summaries[chapterData.id] ? '<em>요약</em>' : "";
        return `
          <button class="chapter-button${active}" type="button" data-chapter="${chapterData.id}">
            <strong>${chapterData.title}${hasSummary}</strong>
            <span>${chapterData.stats.paragraphs}문단 · ${chapterData.stats.notes}주석 · ${chapterData.stats.images}이미지</span>
          </button>
        `;
      })
      .join("") || '<p class="empty">검색 결과가 없습니다.</p>';
}

function renderChapter() {
  const volume = activeVolume();
  const chapterData = volume.chapters.find((item) => item.id === state.chapterId);
  if (!chapterData) {
    chapter.innerHTML = '<p class="empty">표시할 항목이 없습니다.</p>';
    notesList.innerHTML = "";
    return;
  }

  const paragraphs = chapterData.paragraphs
    .map((paragraph) => {
      const alignClass = paragraph.align === "center" ? " center" : "";
      return `<p class="paragraph${alignClass}">${highlight(paragraph.html, state.query)}</p>`;
    })
    .join("");

  chapter.innerHTML = `
    <header>
      <h2>${chapterData.title}</h2>
      <div class="chapter-meta">
        <span>${volume.series}</span>
        <span>${chapterData.id}</span>
        <span>${chapterData.stats.paragraphs}문단</span>
        <span>${chapterData.stats.notes}주석</span>
      </div>
    </header>
    ${renderSummaryCard(chapterData)}
    ${paragraphs}
  `;

  notesList.innerHTML =
    chapterData.notes
      .map((note, index) => {
        return `
          <section class="note" id="${note.id}">
            <h3><span>${index + 1}</span><span>${note.type}</span></h3>
            <p>${highlight(note.html, state.query)}</p>
          </section>
        `;
      })
      .join("") || '<p class="empty">이 항목에는 주석이 없습니다.</p>';
}

function render() {
  renderSummary();
  renderTabs();
  renderChapterList();
  renderChapter();
}

volumeTabs.addEventListener("click", (event) => {
  const button = event.target.closest("[data-volume]");
  if (!button) return;
  state.volumeIndex = Number(button.dataset.volume);
  state.chapterId = null;
  render();
});

chapterList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-chapter]");
  if (!button) return;
  state.chapterId = button.dataset.chapter;
  renderChapterList();
  renderChapter();
  document.querySelector(".reader").scrollIntoView({ behavior: "smooth", block: "start" });
});

searchInput.addEventListener("input", (event) => {
  state.query = event.target.value.trim();
  renderChapterList();
  renderChapter();
});

chapter.addEventListener("click", (event) => {
  const ref = event.target.closest(".note-ref");
  if (!ref) return;
  const target = document.querySelector(`#${ref.dataset.noteId}`);
  target?.scrollIntoView({ behavior: "smooth", block: "center" });
});

toggleNotes.addEventListener("click", () => {
  document.body.classList.toggle("notes-collapsed");
  toggleNotes.setAttribute(
    "aria-label",
    document.body.classList.contains("notes-collapsed") ? "주석 펼치기" : "주석 접기",
  );
});

render();
