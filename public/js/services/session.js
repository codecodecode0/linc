let session = null;

export const getSession = () => session;
export const setSession = (nextSession) => {
  session = nextSession;
};
export const clearSession = () => {
  session = null;
};

