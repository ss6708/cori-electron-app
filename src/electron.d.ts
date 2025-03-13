interface Window {
  require: (module: string) => unknown;
  electronAPI?: {
    embedExcelWindow: (targetId: string) => Promise<{success: boolean, message: string}>;
  };
}

declare namespace NodeJS {
  interface Global {
    require: (module: string) => unknown;
  }
}
