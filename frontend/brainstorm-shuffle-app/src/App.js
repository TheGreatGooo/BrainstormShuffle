import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Box,
} from '@mui/material';

const App = () => {
  const [username, setUsername] = useState('');
  const [state, setState] = useState(0);
  const [secondsRemaining, setSecondsRemaining] = useState(0);
  const [idea, setIdea] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [registeredUser, setRegisteredUser] = useState('');

  useEffect(() => {
    const storedUsername = localStorage.getItem('registeredUser');
    if (storedUsername) {
      setUsername(storedUsername);
      setRegisteredUser(username);
    }
  }, []);

  const registerUser = async () => {
    try {
      const response = await axios.post('backend/register', { name: username, role: "na" });
      if (response.status === 201) {
        localStorage.setItem('registeredUser', username);
        setRegisteredUser(username);
      }
    } catch (error) {
      if (error.response){
        setErrorMsg(error.response.data.msg);
        console.log(error.response.data.msg);
      }else{
        setErrorMsg("Something bad happened: " + error);
        console.log("Something bad happened: " + error);
      }
    }
  };

  const loginUser = async () => {
    try {
      const response = await axios.post('backend/login', { name: username, role: "na" });
      if (response.status === 201) {
        localStorage.setItem('registeredUser', username);
        setRegisteredUser(username);
      }
    } catch (error) {
      if (error.response){
        setErrorMsg(error.response.data.msg);
        console.log(error.response.data.msg);
      }else{
        setErrorMsg("Something bad happened: " + error);
        console.log("Something bad happened: " + error);
      }
    }
  };

  const getState = async () => {
    try {
      const response = await axios.get('backend/state', { params: { user: registeredUser } });
      const { state } = response.data;
      setState(state);
      if (state === 1) {
        setSecondsRemaining(response.data.seconds_remaining);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const postIdea = async (newIdea) => {
    try {
      await axios.post('/idea', { username: newIdea });
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      if (registeredUser) {
        getState();
      }
    }, 5000);

    return () => clearInterval(intervalId);
  }, [username]);

  useEffect(() => {
    if (state === 1 && secondsRemaining > 0) {
      const timerId = setInterval(() => {
        setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
      return () => clearInterval(timerId);
    }
  }, [state, secondsRemaining]);

  const handleIdeaChange = (e) => {
    const newIdea = e.target.value;
    setIdea(newIdea);
    postIdea(newIdea);
  };

  return (
    <Container>
      {state === 0 && !registeredUser && (
        <Box textAlign="center" mt={5}>
          <Typography variant="h4">Register</Typography>
          <TextField
            variant="outlined"
            label="Enter your name"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
          />
          <Button variant="contained" color="primary" onClick={registerUser}>
            Register
          </Button>
          <Button variant="contained" color="primary" onClick={loginUser}>
            Login
          </Button>
          {errorMsg && <Typography color="error">{errorMsg}</Typography>}
        </Box>
      )}

      {state === 1 && (
        <Box textAlign="center" mt={5}>
          <Typography variant="h4">Next Round Starting!</Typography>
          <Typography variant="h5">
            {`Time Remaining: ${Math.floor(secondsRemaining / 60)}:${String(secondsRemaining % 60).padStart(2, '0')}`}
          </Typography>
          <TextField
            variant="outlined"
            label="What idea are you passionate about?"
            value={idea}
            onChange={handleIdeaChange}
            margin="normal"
            fullWidth
            multiline
            rows={4}
          />
        </Box>
      )}

      {(state === 2 || state === 0) && (
        <Box textAlign="center" mt={5}>
          <Typography variant="h4">Waiting for Next Round...</Typography>
          <TextField
            variant="outlined"
            label="What idea are you passionate about?"
            value={idea}
            onChange={handleIdeaChange}
            margin="normal"
            fullWidth
            multiline
            rows={4}
          />
        </Box>
      )}

      {state === 3 && (
        <Box textAlign="center" mt={5}>
          <Typography variant="h4">Thank You!</Typography>
          <Typography>Your session has ended. Please submit your question.</Typography>
        </Box>
      )}

      {state === 1 && (
        <CircularProgress />
      )}
    </Container>
  );
};

export default App;
