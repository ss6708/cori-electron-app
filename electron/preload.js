const { contextBridge } = 'electron';
contextBridge.exposeInMainWorld('api', {
  // Expose secure API methods here
  sendMessage: (message) => {
    console.log('Received message:', message);
  },
});