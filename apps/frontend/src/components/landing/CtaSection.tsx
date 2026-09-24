import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Button } from '../ui/Button';

export const CtaSection: React.FC = () => {
  return (
    <section className="py-20 text-center">
      <div className="max-w-xl mx-auto px-4">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white font-display mb-4">
          Ready to speak with confidence?
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-8">
          Join thousands of learners practicing daily Spanish, French, and Japanese.
        </p>
        <Link to="/register">
          <Button size="xl" variant="primary" rightIcon={<ArrowRight className="w-5 h-5" />}>
            CREATE FREE ACCOUNT
          </Button>
        </Link>
      </div>
    </section>
  );
};
