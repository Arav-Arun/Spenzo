// Product and mascot names live here, so a rename is a one-line change.
export const NAME = 'Spenzo';
export const MASCOT = 'Baaz';

// Spenzo's WhatsApp number (digits only); VITE_WHATSAPP_NUMBER overrides it for another deployment.
const WHATSAPP_NUMBER = import.meta.env.VITE_WHATSAPP_NUMBER || '919820223725';
export const whatsappLink = (text = 'Hi') => `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;

export const API_URL = import.meta.env.VITE_API_URL || '';
