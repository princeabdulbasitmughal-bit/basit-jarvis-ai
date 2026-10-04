import express from 'express';
import { jwtMiddleware } from './middleware/jwtMiddleware';

const app = express();

app.use(express.json());

// Protected route
app.get('/protected', jwtMiddleware, (req, res) => {
  res.json({ message: 'This is a protected route', user: req.user });
});

// Public route
app.get('/public', (req, res) => {
  res.json({ message: 'This is a public route' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
