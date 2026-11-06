import { StateField, StateEffect } from '@codemirror/state';
import { EditorView, Decoration} from '@codemirror/view';
import type { DecorationSet } from '@codemirror/view';

// Effect to update issues
export const setIssuesEffect = StateEffect.define<{ line: number, severity: string }[]>();

// The StateField that holds the decorations
export const issueAnnotations = StateField.define<DecorationSet>({
  create() {
    return Decoration.none;
  },
  update(decorations, tr) {
    decorations = decorations.map(tr.changes);
    
    for (let e of tr.effects) {
      if (e.is(setIssuesEffect)) {
        const marks = [];
        for (const issue of e.value) {
          if (issue.line > 0 && issue.line <= tr.state.doc.lines) {
            const line = tr.state.doc.line(issue.line);
            const className = issue.severity === 'critical' ? 'cm-issue-critical' :
                              issue.severity === 'error' ? 'cm-issue-error' :
                              'cm-issue-warning';
            marks.push(Decoration.line({ class: className }).range(line.from));
          }
        }
        return Decoration.set(marks);
      }
    }
    return decorations;
  },
  provide: f => EditorView.decorations.from(f)
});

// The CSS for the highlighting
export const annotationTheme = EditorView.theme({
  ".cm-issue-critical": { backgroundColor: "rgba(255,92,138,0.28)", borderLeft: "3px solid #FF5C8A" },
  ".cm-issue-error": { backgroundColor: "rgba(255,143,184,0.16)", borderLeft: "3px solid #FF8FB8" },
  ".cm-issue-warning": { backgroundColor: "rgba(255,143,184,0.16)", borderLeft: "3px solid #FF8FB8" },
});