import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import "./App.css";
import { themeOptions } from "./theme";
import { ThemeProvider } from "@mui/material";

ReactDOM.render(
  <ThemeProvider theme={themeOptions}>
    <App />
  </ThemeProvider>,
  document.getElementById("root")
);
