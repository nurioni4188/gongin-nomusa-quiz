(() => {
  "use strict";
  const catalog = window.N27_CATALOG.items;
  const source = window.NOMUSA_AUTO_SOURCE;
  const byId = new Map(catalog.map(item => [item.id, item]));
  if (byId.size !== catalog.length) throw new Error("Duplicate baseline ID");
  for (const match of source.reconciled2013) {
    const item = byId.get(match.id);
    if (!item || item.year !== 2013 || item.subject !== match.subject || item.pdfPage !== match.page) {
      throw new Error("2013 source mapping conflict: " + match.id);
    }
    item.historicalSource = match.questions;
  }
  for (const question of source.historical) {
    if (byId.has(question.id)) throw new Error("Duplicate historical ID: " + question.id);
    const filename = source.sources.find(entry => entry.year === question.year).filename;
    const item = {
      id: question.id, year: question.year, subject: question.subject,
      topic: "제" + question.round + "회 · 문제 " + question.number,
      points: question.points ?? "미확정", sourceOnly: true, approved: false,
      answerStatus: "HOLD", sourceStatus: "HWP_EXTRACT_REVIEW_PENDING", sections: [],
      basis: filename + " · 추출문 " + question.lines[0] + "행부터 · 원본 쪽·시각자료 HOLD",
      sourceText: [question.text, ...question.subquestions.map(part => part.text)].join("\n\n"),
      historicalSource: [question],
    };
    byId.set(item.id, item);
    catalog.push(item);
  }
})();
