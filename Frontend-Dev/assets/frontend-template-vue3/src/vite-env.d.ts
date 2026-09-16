/// <reference types="vite/client" />

/** 环境变量类型：新增 VITE_ 前缀变量在 .env 与此处同步声明，拼错/漏配编译期即报 */
interface ImportMetaEnv {
  /** 后端 API 前缀（request.ts 读取；见 .env.example） */
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
