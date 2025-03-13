interface Window {
  require: (module: string) => unknown;
}

declare namespace NodeJS {
  interface Global {
    require: (module: string) => unknown;
  }
}
