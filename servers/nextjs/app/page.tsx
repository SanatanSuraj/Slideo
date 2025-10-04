'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { Github, Cloud, Star, Calendar, ArrowRight, Check, ChevronRight, ChevronDown, LogOut } from 'lucide-react';
import { RootState } from '../store/store';
import { logout } from '../store/slices/authSlice';

export default function HomePage() {
    const router = useRouter();
    const dispatch = useDispatch();
    const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);

    const handleGetPPT = () => {
        if (!isAuthenticated) {
            router.push('/auth/login');
        } else {
            router.push('/upload');
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        dispatch(logout());
    };

    return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">P</span>
          </div>
          <span className="text-xl font-semibold text-gray-900">Presenton</span>
        </div>
        
        <nav className="hidden md:flex items-center space-x-8">
          <Link href="/docs" className="text-gray-600 hover:text-gray-900">Docs</Link>
          <Link href="/blogs" className="text-gray-600 hover:text-gray-900">Blogs</Link>
          <Link href="/pricing" className="text-gray-600 hover:text-gray-900">Pricing</Link>
          <Link href="/book-call" className="flex items-center space-x-1 text-gray-600 hover:text-gray-900">
            <Calendar className="w-4 h-4" />
            <span>Book Call</span>
          </Link>
          {isAuthenticated ? (
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.name}</span>
              <button 
                onClick={handleLogout}
                className="flex items-center space-x-1 bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <Link href="/auth/login" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-lg font-medium">
              Login
            </Link>
          )}
        </nav>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center">
          {/* Public Beta Badge */}
          <div className="inline-flex items-center px-3 py-1 rounded-full border border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 text-sm font-medium text-purple-700 mb-6">
            Public Beta
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Open-Source AI<br />
            Presentation Generator
          </h1>

          {/* Tagline */}
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Self-host, integrate via API, and generate pixel-perfect decks in minutes. No vendor lock-in.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button 
              onClick={handleGetPPT}
              className="flex items-center justify-center space-x-2 bg-gray-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors"
            >
              <Cloud className="w-5 h-5" />
              <span>Get your PPT</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <Link href="/template-preview" className="flex items-center justify-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-colors">
              <Github className="w-5 h-5" />
              <span>Get Landing Page</span>
              <Star className="w-4 h-4" />
            </Link>
          </div>

          {/* Feature Highlights */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-8 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>Clean API</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>Custom Template</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>2,364 GitHub Stars</span>
              <Star className="w-4 h-4 text-yellow-500" />
            </div>
          </div>
        </div>
      </section>

      {/* How Presenton Solves This Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="text-green-600 text-sm font-medium mb-4">How Presenton Solves This</div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">One solution, complete control</h2>
              
              {/* Tabs */}
              <div className="flex space-x-8 mb-8">
                <button className="flex items-center space-x-2 text-gray-900 border-b-2 border-gray-900 pb-2">
                  <div className="w-5 h-5 bg-gray-900 rounded"></div>
                  <span>For Business Teams</span>
                </button>
                <button className="flex items-center space-x-2 text-gray-500 hover:text-gray-700">
                  <div className="w-5 h-5 border border-gray-300 rounded"></div>
                  <span>For Developers</span>
                </button>
              </div>

              <p className="text-lg text-gray-600 mb-8">
                Empower your teams to create consistent, compliant, and professional presentations — all within your secure environment.
              </p>

              {/* Feature Cards */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-2xl font-bold text-blue-600 mb-2">Snappy</h3>
                  <p className="text-gray-600">Generate pixel-perfect presentations in minutes, not hours.</p>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-purple-600 mb-2">Consistency</h3>
                  <p className="text-gray-600">Custom templates ensure every deck stays on-brand, every time.</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600 to-purple-700 rounded-2xl p-8 text-white">
              <div className="text-center">
                <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <div className="w-8 h-8 bg-white rounded"></div>
                </div>
                <div className="space-y-4 text-sm">
                  <div className="flex items-start space-x-3">
                    <Check className="w-5 h-5 text-green-400 mt-0.5" />
                    <span>Air-gapped deployment options for financial institutions and organizations with strict regulatory requirements.</span>
                  </div>
                  <div className="flex items-start space-x-3">
                    <Check className="w-5 h-5 text-green-400 mt-0.5" />
                    <span>Generate professional presentations in minutes, not hours.</span>
                  </div>
                  <div className="flex items-start space-x-3">
                    <Check className="w-5 h-5 text-green-400 mt-0.5" />
                    <span>Custom templates ensure every presentation aligns with your brand guidelines and corporate identity.</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Essential Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Essential Features</h2>
            <p className="text-lg text-gray-600">Built for developers needing control over presentation generation workflow.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-gray-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-6 h-6 border border-gray-900 rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Custom Template Support</h3>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-gray-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-gray-900 font-mono">&lt; &gt;</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">API-First Architecture</h3>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-gray-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-6 h-6 bg-gray-900 rounded-full"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Beautiful In-built Templates</h3>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-gray-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-gray-900 font-mono">&gt; _</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">One-Command Deploy</h3>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-gray-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-6 h-6 bg-gray-900 rounded-full"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Integration</h3>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-gray-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <div className="w-6 h-6 border border-gray-900 rounded-full"></div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">MCP Support</h3>
            </div>
          </div>
        </div>
      </section>

      {/* One Engine Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center">
            <div className="text-red-600 text-sm font-medium mb-4">Eyebrow: For Developers and Teams</div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">One engine for Developers and teams</h2>
            <h3 className="text-4xl font-bold text-gray-900 mb-8">deploy your way</h3>
            <p className="text-lg text-gray-600 max-w-4xl mx-auto mb-12">
              Embed generation with a clean API, or run the same open-source engine for your team in our managed cloud or self-hosted. Your templates, your data, zero lock-in.
            </p>

            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-gray-900">Developers: Ship with a clean API</span>
                </div>
                <p className="text-gray-600">Generate and update decks from your data and workflows; integrate in minutes.</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-gray-900">Managed cloud for speed</span>
                </div>
                <p className="text-gray-600">Collaborative browser UI and instant scale—no ops required.</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-gray-900">Your templates, your brand</span>
                </div>
                <p className="text-gray-600">Upload your existing PPTX or PDF files to create templates with AI. Then generate AI presentations over it.</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center space-x-3 mb-4">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-gray-900">Self-host for control</span>
                </div>
                <p className="text-gray-600">Run on your infrastructure for privacy and compliance.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Use Cases</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl shadow-sm border">
              <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 mb-6">
                <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-gray-900 rounded"></div>
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">custom deployments for enterprise</h3>
              <div className="text-sm font-semibold text-gray-900 mb-2">Free Presentation Generation</div>
              <p className="text-gray-600 italic mb-6">I want to generate presentations locally in private for free</p>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Can run completely offline with Ollama</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Integrate with your favourite LLM providers</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Add most capable image generation models</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border">
              <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 mb-6">
                <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-gray-900 rounded"></div>
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">client reports on auto</h3>
              <div className="text-sm font-semibold text-gray-900 mb-2">Financial Services</div>
              <p className="text-gray-600 italic mb-6">We need 200 client reports weekly, all compliant and on-brand</p>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Automated generation via API</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Air-gapped deployment for compliance</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Custom templates for brand consistency</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border">
              <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 mb-6">
                <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-blue-600 rounded text-white text-xs flex items-center justify-center">SaaS</div>
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">ai presentation as integration</h3>
              <div className="text-sm font-semibold text-gray-900 mb-2">SaaS Companies</div>
              <p className="text-gray-600 italic mb-6">Our customers want presentation generation in our product</p>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">White-label integration</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">API for seamless embedding</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-600">Custom templates for customer branding</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-8">Frequently asked questions</h2>
            </div>
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">What is Presenton and how is it different from typical slide tools?</span>
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                </button>
                <p className="mt-3 text-gray-600">
                  Presenton is an open-source AI presentation generator that stands out from typical slide tools through its complete customization capabilities using custom templates and built-in presentation automation features.
                </p>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">Who is Presenton for—developers embedding slides or teams creating them in the UI?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">What file formats do you output (PPTX, PDF) and are decks fully editable afterward?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">How do I bring my own templates and brand assets?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">Do you support charts, tables, images, and data-driven components?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">Can I control fonts, colors, and layout rules globally?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">Is my data used to train models?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="border-b border-gray-200 pb-4">
                <button className="flex items-center justify-between w-full text-left">
                  <span className="font-medium text-gray-900">How do I contact for custom deployment support?</span>
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-1">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">P</span>
                </div>
                <span className="text-xl font-semibold">Presenton</span>
              </div>
              <p className="text-gray-400 mb-4">
                Presenton is the open-source AI presentation engine private, and fully customizable. Bring your templates and brand; self-host or embed via API with no lock-in.
              </p>
              <p className="text-gray-400 text-sm">Presenton with AI - at its best</p>
              <p className="text-gray-400 text-sm mt-4">Presenton Inc. 8 The Green, STE R, Dover, DE 19901, USA</p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Community</h3>
              <div className="space-y-2 text-gray-400">
                <Link href="/docker" className="block hover:text-white">Docker</Link>
                <Link href="/docs" className="block hover:text-white">Docs</Link>
                <Link href="/github" className="block hover:text-white">GitHub</Link>
                <Link href="/support" className="block hover:text-white">Support</Link>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <div className="space-y-2 text-gray-400">
                <Link href="/features" className="block hover:text-white">Features</Link>
                <Link href="/developers" className="block hover:text-white">For Developers</Link>
                <Link href="/business" className="block hover:text-white">For Business</Link>
                <Link href="/use-cases" className="block hover:text-white">Use Cases</Link>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Join our newsletter to stay up to date on features and releases.</h3>
              <div className="flex space-x-2 mb-4">
                <input 
                  type="email" 
                  placeholder="Email" 
                  className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-400"
                />
                <button className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                  Submit
                </button>
              </div>
              <p className="text-gray-400 text-xs mb-4">
                By subscribing, you consent to receive updates from our company and agree to our privacy policy.
              </p>
              <p className="text-gray-400 text-xs">© 2025 Presenton Inc. All rights reserved.</p>
              <div className="flex space-x-4 mt-2">
                <Link href="/privacy" className="text-gray-400 text-xs hover:text-white">Privacy Policy</Link>
                <Link href="/terms" className="text-gray-400 text-xs hover:text-white">Terms and Conditions</Link>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}