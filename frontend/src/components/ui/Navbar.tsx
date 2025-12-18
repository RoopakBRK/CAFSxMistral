'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { ShieldCheck, Menu, X, Activity } from 'lucide-react';


export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 0);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav
      className={`
        fixed top-0 left-0 right-0 z-50
        transition-colors duration-300
        ${scrolled ? 'bg-white shadow-md' : 'bg-transparent'}
      `}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="bg-orange-600 p-1.5 rounded-lg group-hover:bg-orange-500 transition-colors">
              <ShieldCheck className="w-10 h-10 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900">
              SKILL<span className="text-orange-600">KENDRA</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              href="/"
              className="text-sm font-medium text-slate-700 hover:text-orange-500 transition-colors"
            >
              Home
            </Link>
            <Link
              href="/#verify"
              className="text-sm font-medium text-slate-700 hover:text-orange-500 transition-colors"
            >
              Verify
            </Link>
            <Link
              href="/recent-activity"
              className="inline-flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-orange-500 transition-colors"
            >
              <Activity className="w-4 h-4" />
              Activity
            </Link>
            <Link
              href="/#about"
              className="text-sm font-medium text-slate-700 hover:text-orange-500 transition-colors"
            >
              About
            </Link>

            <Link
              href="/profile"
              className="px-5 py-2.5 rounded-full bg-orange-600 text-white text-sm font-semibold hover:bg-orange-700 transition-colors shadow-md hover:shadow-lg"
            >
              Profile
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-black/5 transition-colors"
            aria-label="Toggle menu"
          >
            {isOpen ? (
              <X className="w-6 h-6 text-slate-900" />
            ) : (
              <Menu className="w-6 h-6 text-slate-900" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-white border-t border-slate-200 shadow-lg p-4 space-y-2">
            <Link
              href="/"
              className="block px-4 py-3 text-slate-700 hover:bg-slate-100 hover:text-orange-500 rounded-lg transition-colors font-medium"
              onClick={() => setIsOpen(false)}
            >
              Home
            </Link>
            <Link
              href="/#verify"
              className="block px-4 py-3 text-slate-700 hover:bg-slate-100 hover:text-orange-500 rounded-lg transition-colors font-medium"
              onClick={() => setIsOpen(false)}
            >
              Verify
            </Link>
            <Link 
              href="/recent-activity"
              className="flex items-center gap-2 px-4 py-3 text-slate-700 hover:bg-slate-100 hover:text-orange-500 rounded-lg transition-colors font-medium"
              onClick={() => setIsOpen(false)}
            >
              <Activity className="w-5 h-5" />
              Recent Activity
            </Link>
            <Link
              href="/#about"
              className="block px-4 py-3 text-slate-700 hover:bg-slate-100 hover:text-orange-500 rounded-lg transition-colors font-medium"
              onClick={() => setIsOpen(false)}
            >
              About
            </Link>
            <Link
              href="/profile"
              className="block w-full text-center px-4 py-3 bg-orange-600 text-white rounded-lg font-bold hover:bg-orange-700 transition-colors mt-2"
              onClick={() => setIsOpen(false)}
            >
              Profile
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
