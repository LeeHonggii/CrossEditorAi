if (typeof (window as any).process === 'undefined') {
    (window as any).process = { env: { NODE_ENV: 'development' } };
}

export { };
