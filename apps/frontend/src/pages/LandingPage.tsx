import React from 'react';
import {
  HeroSection,
  InteractivePreviewSection,
  HowItWorksSection,
  ExerciseTypesSection,
  CtaSection,
  Footer,
} from '../components/landing';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">
      <HeroSection />
      <HowItWorksSection />
      <ExerciseTypesSection />
      <CtaSection />
      <Footer />
    </div>
  );
};
