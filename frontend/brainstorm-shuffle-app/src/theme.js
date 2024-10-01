import { createTheme } from "@mui/material/styles";

export const themeOptions = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#ff7a59",
    },
    secondary: {
      main: "#00a4bd",
    },
    error: {
      main: "#f2545b",
    },
    warning: {
      main: "#f5c26b",
    },
    info: {
      main: "#00a4bd",
    },
    success: {
      main: "#00bda5",
    },
    text: {
      primary: "#33475b",
    },
    background: {
      default: "#f5f8fa",
    },
  },
});
