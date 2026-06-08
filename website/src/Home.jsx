import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Showcases from './components/Showcases';
import QuickStart from './components/QuickStart';
import ScreenshotGallery from './components/ScreenshotGallery';
import MasonryGallery from './components/MasonryGallery';
import Features from './components/Features';
import Web3Edge from './components/Web3Edge';
import Footer from './components/Footer';

const CLAUDE_IMGS = Array.from({ length: 13 }, (_, i) => `/screenshots/img${i + 1}.png`);
const WHATSAPP_IMGS = [
  "/screenshots/IMG_0712.PNG",
  "/screenshots/IMG_0713.PNG",
  "/screenshots/IMG_0721.PNG",
  "/screenshots/IMG_0722.PNG",
  "/screenshots/IMG_0723.PNG",
  "/screenshots/IMG_0724.PNG",
  "/screenshots/IMG_0725.PNG"
];

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-[#f0f0f0] flex flex-col font-sans selection:bg-[#a7dd5d] selection:text-black overflow-x-hidden relative">
      <Header />
      <Hero />
      <Showcases />
      <QuickStart />
      
      <ScreenshotGallery 
        title="WhatsApp Integration in Action" 
        subtitle="Real screenshots of Spenzo functioning perfectly on WhatsApp. Tap to expand." 
        images={WHATSAPP_IMGS} 
      />
      
      <div className="sm:hidden">
        <ScreenshotGallery 
          title="Spenzo MCP in Claude Desktop" 
          subtitle="Real screenshots of Spenzo running live inside Claude Desktop. Tap any image to rotate or expand." 
          images={CLAUDE_IMGS} 
        />
      </div>
      <div className="hidden sm:block">
        <MasonryGallery 
          title="Spenzo MCP in Claude Desktop" 
          subtitle="Real screenshots of Spenzo running live inside Claude Desktop. Click any image to expand." 
          images={CLAUDE_IMGS} 
        />
      </div>

      <Features />
      <Web3Edge />
      <Footer />
    </div>
  );
}
