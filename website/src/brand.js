// Product and mascot names live here, so a rename is a one-line change.
export const NAME = 'Spenzo';
export const MASCOT = 'Baaz';
export const TAGLINE = 'Your money buddy on WhatsApp';

// Until your own WhatsApp Business number is live, this is the Twilio sandbox number.
export const WHATSAPP_NUMBER = import.meta.env.VITE_WHATSAPP_NUMBER || '919820223725';
export const whatsappLink = (text = 'Hi') => `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;

export const API_URL = import.meta.env.VITE_API_URL || '';
export const GITHUB = 'https://github.com/Arav-Arun/Spenzo';
