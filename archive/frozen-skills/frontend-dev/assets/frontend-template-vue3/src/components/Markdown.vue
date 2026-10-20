<script lang="ts">
import { createTextVNode, Fragment, defineComponent, h, type VNode } from 'vue';

/**
 * 轻量 Markdown 渲染（AI 回复展示用，零依赖）——与 React 版同构移植。
 * 覆盖 AI 回答高频语法：标题/无序·有序列表/表格/围栏代码块/粗体/行内代码；
 * 直接产出 VNode（不走 v-html，天然免 XSS）。
 */
export default defineComponent({
  name: 'AppMarkdown',
  props: {
    /** Markdown 源文本（可能为空串） */
    text: { type: String, required: true },
  },
  setup(props) {
    return () => h(Fragment, parseBlocks(props.text ?? ''));
  },
});

let key = 0;

/** 块级解析：按行切分，识别围栏代码/表格/列表/标题/段落 */
function parseBlocks(text: string): VNode[] {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const blocks: VNode[] = [];
  key = 0;
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === '') {
      i += 1;
      continue;
    }
    // 围栏代码块 ```lang ... ```
    if (line.trimStart().startsWith('```')) {
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].trimStart().startsWith('```')) {
        code.push(lines[i]);
        i += 1;
      }
      i += 1; // 跳过收尾 ```
      blocks.push(
        h(
          'pre',
          { key: key++, style: { background: 'var(--color-primary-subtle)', padding: '8px', borderRadius: '6px', overflowX: 'auto', margin: '4px 0' } },
          [h('code', code.join('\n'))],
        ),
      );
      continue;
    }
    // 表格：当前行与下一行都含 | 且下一行是分隔行（---）
    if (
      line.includes('|') &&
      i + 1 < lines.length &&
      lines[i + 1].includes('|') &&
      /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1]) &&
      lines[i + 1].includes('-')
    ) {
      const cells = splitTableRow(line);
      const rows: string[][] = [];
      i += 2;
      while (i < lines.length && lines[i].includes('|') && lines[i].trim() !== '') {
        rows.push(splitTableRow(lines[i]));
        i += 1;
      }
      blocks.push(
        h(
          'table',
          { key: key++, style: { borderCollapse: 'collapse', margin: '4px 0' } },
          [
            h('thead', [
              h('tr', cells.map((c, ci) => h('th', { key: ci, style: cellStyle }, parseInline(c)))),
            ]),
            h(
              'tbody',
              rows.map((r, ri) =>
                h('tr', { key: ri }, r.map((c, ci) => h('td', { key: ci, style: cellStyle }, parseInline(c)))),
              ),
            ),
          ],
        ),
      );
      continue;
    }
    // 标题 # ~ ####
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      blocks.push(
        h('div', { key: key++, style: { fontWeight: 600, margin: '6px 0 2px' } }, parseInline(heading[2])),
      );
      i += 1;
      continue;
    }
    // 无序列表（含缩进两层）
    if (/^\s*[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ''));
        i += 1;
      }
      blocks.push(
        h('ul', { key: key++, style: ulStyle }, items.map((it, ii) => h('li', { key: ii }, parseInline(it)))),
      );
      continue;
    }
    // 有序列表
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''));
        i += 1;
      }
      blocks.push(
        h('ol', { key: key++, style: ulStyle }, items.map((it, ii) => h('li', { key: ii }, parseInline(it)))),
      );
      continue;
    }
    // 段落：连续非空非特殊行合并
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !lines[i].trimStart().startsWith('```') &&
      !/^\s*([-*]|\d+\.)\s+/.test(lines[i]) &&
      !/^#{1,4}\s+/.test(lines[i])
    ) {
      para.push(lines[i]);
      i += 1;
    }
    blocks.push(
      h(
        'p',
        { key: key++, style: { margin: '4px 0', whiteSpace: 'pre-wrap' } },
        parseInline(para.join('\n')),
      ),
    );
  }
  return blocks;
}

const cellStyle = { border: '1px solid var(--color-border)', padding: '2px 8px' };
const ulStyle = { paddingLeft: '20px', margin: '4px 0' };

/** 表格行按 | 切分（去掉首尾空单元格） */
function splitTableRow(line: string): string[] {
  const cells = line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|');
  return cells.map((c) => c.trim());
}

/** 行内解析：`code`、**bold**；其余按纯文本 */
function parseInline(text: string): VNode[] {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).filter((p) => p !== '');
  return parts.map((p, i) => {
    if (p.startsWith('`') && p.endsWith('`') && p.length > 2) {
      return h(
        'code',
        { key: i, style: { background: 'var(--color-primary-subtle)', padding: '0 4px', borderRadius: '4px' } },
        p.slice(1, -1),
      );
    }
    if (p.startsWith('**') && p.endsWith('**') && p.length > 4) {
      return h('strong', { key: i }, p.slice(2, -2));
    }
    // Fragment 子级必须是数组，纯文本用 createTextVNode 包装
    return h(Fragment, { key: i }, [createTextVNode(p)]);
  });
}
</script>
