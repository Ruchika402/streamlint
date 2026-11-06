import { EditorView } from '@codemirror/view'
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { tags as t } from '@lezer/highlight'
import { issueAnnotations, annotationTheme } from './annotations' // <-- ADD THIS

export const streamlintTheme = EditorView.theme({
  "&": { backgroundColor: "var(--code-bg)", color: "var(--code-text)", fontSize: "14px", fontFamily: "'JetBrains Mono', monospace" },
  ".cm-content": { caretColor: "#FF9ECB", padding: "16px 0" },
  ".cm-gutters": { backgroundColor: "var(--code-bg)", color: "var(--code-gutter)", border: "none", minWidth: "44px" },
  ".cm-activeLine": { backgroundColor: "rgba(255,255,255,0.04)" },
  ".cm-selectionBackground, ::selection": { backgroundColor: "rgba(255,143,184,0.3) !important" }
}, { dark: true })

export const streamlintHighlight = HighlightStyle.define([
  { tag: t.keyword, color: "var(--tok-keyword)" },
  { tag: [t.string, t.number], color: "var(--tok-string)" },
  { tag: [t.function(t.variableName), t.className], color: "var(--tok-fn)" },
  { tag: t.comment, color: "#B79BB0", fontStyle: "italic" },
])

export const streamlintExtensions = [
  streamlintTheme, 
  syntaxHighlighting(streamlintHighlight),
  issueAnnotations, // <-- MAKE SURE THIS IS HERE
  annotationTheme   // <-- MAKE SURE THIS IS HERE
]