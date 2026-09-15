import { Fragment, type ReactNode } from 'react';

/**
 * 轻量 Markdown 渲染（AI 回复展示用，零依赖）。
 * 覆盖 AI 回答高频语法：标题/无序·有序列表/表格/围栏代码块/粗体/行内代码；直接产出 JSX（不走 dangerouslySetInnerHTML，天然免 XSS）。
 * @param text Markdown 源文本（可能为空串）
 * @returns 渲染后的块级元素数组
 */
export default function Markdown({ text }: { text: string }) {
  return <>{parseBlocks(text ?? '')}</>;
}

/** 块级解析：按行切分，识别围栏代码/表格/列表/标题/段落 */
function parseBlocks(text: string): ReactNode[] {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const blocks: ReactNode[] = [];
  let i = 0;
  let key = 0;
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
        <pre
          key={key++}
          style={{ background: '#f6f8fa', padding: 8, borderRadius: 6, overflowX: 'auto', margin: '4px 0' }}
        >
          <code>{code.join('\n')}</code>
        </pre>,
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
        <table key={key++} style={{ borderCollapse: 'collapse', margin: '4px 0' }}>
          <thead>
            <tr>
              {cells.map((c, ci) => (
                <th key={ci} style={{ border: '1px solid #d9d9d9', padding: '2px 8px' }}>
                  {parseInline(c)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, ri) => (
              <tr key={ri}>
                {r.map((c, ci) => (
                  <td key={ci} style={{ border: '1px solid #d9d9d9', padding: '2px 8px' }}>
                    {parseInline(c)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>,
      );
      continue;
    }
    // 标题 # ~ ####
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      blocks.push(
        <div key={key++} style={{ fontWeight: 600, margin: '6px 0 2px' }}>
          {parseInline(heading[2])}
        </div>,
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
        <ul key={key++} style={{ paddingLeft: 20, margin: '4px 0' }}>
          {items.map((it, ii) => (
            <li key={ii}>{parseInline(it)}</li>
          ))}
        </ul>,
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
        <ol key={key++} style={{ paddingLeft: 20, margin: '4px 0' }}>
          {items.map((it, ii) => (
            <li key={ii}>{parseInline(it)}</li>
          ))}
        </ol>,
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
      <p key={key++} style={{ margin: '4px 0', whiteSpace: 'pre-wrap' }}>
        {parseInline(para.join('\n'))}
      </p>,
    );
  }
  return blocks;
}

/** 表格行按 | 切分（去掉首尾空单元格） */
function splitTableRow(line: string): string[] {
  const cells = line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|');
  return cells.map((c) => c.trim());
}

/** 行内解析：`code`、**bold**；其余按纯文本 */
function parseInline(text: string): ReactNode {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).filter((p) => p !== '');
  return (
    <>
      {parts.map((p, i) => {
        if (p.startsWith('`') && p.endsWith('`') && p.length > 2) {
          return (
            <code key={i} style={{ background: '#f0f0f0', padding: '0 4px', borderRadius: 4 }}>
              {p.slice(1, -1)}
            </code>
          );
        }
        if (p.startsWith('**') && p.endsWith('**') && p.length > 4) {
          return <strong key={i}>{p.slice(2, -2)}</strong>;
        }
        return <Fragment key={i}>{p}</Fragment>;
      })}
    </>
  );
}
