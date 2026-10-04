import jwt from 'jsonwebtoken';

export const generateToken = (payload: object, expiresIn: string = '1h') => {
  return jwt.sign(payload, process.env.JWT_SECRET as string, { expiresIn });
};
