import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Situation } from '../types';

interface UserState {
  userId: string;
  situation: Situation | null;
  setUserId: (id: string) => void;
  setSituation: (situation: Situation) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      userId: 'demo_user_001', // Default demo user
      situation: null,
      setUserId: (id) => set({ userId: id }),
      setSituation: (situation) => set({ situation }),
    }),
    {
      name: 'BySideScheme-storage',
    }
  )
);
