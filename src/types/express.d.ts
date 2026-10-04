import { JwtPayload } from '../middleware/jwtMiddleware';

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}
