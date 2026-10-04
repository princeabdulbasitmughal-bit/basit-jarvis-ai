import express from 'express';
import { generateToken } from '../utils/jwtUtils';

const router = express.Router();

router.post('/login', (req, res) => {
  // Validate user credentials (pseudo-code)
  const { username, password } = req.body;

  if (username === 'user' && password === 'password') {
    const token = generateToken({ userId: '123' });
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

export default router;
