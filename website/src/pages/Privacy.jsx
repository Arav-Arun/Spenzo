import Footer from '../components/Footer';
import Header from '../components/Header';
import { NAME } from '../brand';

const CONTACT = 'spenzo@aravarun.in';

const Section = ({ title, children }) => (
  <section className="space-y-3">
    <h2 className="text-xl font-extrabold">{title}</h2>
    {children}
  </section>
);
const List = ({ items }) => (
  <ul className="list-disc space-y-1.5 pl-5">
    {items.map((i) => <li key={typeof i === 'string' ? i : i.key}>{i}</li>)}
  </ul>
);

export default function Privacy() {
  return (
    <div className="min-h-screen font-sans">
      <Header />
      <main className="mx-auto max-w-3xl px-4 pt-14 pb-20 sm:px-6">
        <h1 className="mb-10 text-4xl font-extrabold md:text-5xl">Privacy Policy</h1>

        <div className="space-y-10 text-[16.5px] leading-relaxed text-ink/85">
          <Section title="The short version">
            <List items={[
              `${NAME} only knows what you tell it in chat. It never asks for bank logins, card numbers, PINs or passwords.`,
              'Your data is used to run the service for you. It is never sold, and never used for advertising.',
              'Only you can see your data. Send “delete my data” on WhatsApp at any time to erase it permanently.',
            ]} />
          </Section>

          <Section title="Who we are">
            <p>
              {NAME} (“{NAME}”, “we”, “us”) is a personal finance assistant you use over WhatsApp, with a companion
              dashboard at spenzo.aravarun.in. It is built and run by Arav Arun, an individual based in India. This policy explains
              what information {NAME} collects, why, who it is shared with, and the choices you have. By using {NAME} you
              agree to this policy. If you don’t agree, please don’t use the service.
            </p>
          </Section>

          <Section title="What we collect">
            <p><b>When you message {NAME} on WhatsApp:</b></p>
            <List items={[
              'Your WhatsApp phone number and the profile name WhatsApp shares with businesses. Your number is your account.',
              'The messages you send: text, photos (for example bills or investment screenshots) and voice notes.',
              'What you ask us to keep track of: expenses and income, budgets, savings goals, amounts you owe or are owed along with the names you give for those people, investment holdings, and public crypto wallet addresses.',
              'Things you ask us to remember, such as your name, your monthly income or your salary day.',
              'A UPI ID, only if you share one so we can make payment links for you.',
            ]} />
            <p><b>When you use the website or dashboard:</b></p>
            <List items={[
              'A sign-in token stored in your browser’s local storage so you stay signed in. We don’t use advertising or tracking cookies.',
              'Basic technical logs kept by our hosting providers (such as IP address, browser type and time of request), used for security and to fix problems.',
            ]} />
            <p><b>What we don’t collect:</b> bank or card details, passwords, your contacts, your location, or anything from your phone outside the chat.</p>
          </Section>

          <Section title="How we use it">
            <List items={[
              'To understand your messages and reply: logging transactions, answering questions about your money, and showing your dashboard.',
              'To send helpful nudges inside our replies, like a budget warning or a goal reminder. You can turn these off by sending “stop nudges”.',
              'To keep the service secure, prevent abuse, and fix bugs.',
            ]} />
            <p>We don’t sell your information, show you ads, or share it with anyone for their marketing.</p>
          </Section>

          <Section title="Who we share it with">
            <p>We use a few trusted services to run {NAME}. Each receives only what it needs:</p>
            <List items={[
              <span key="meta"><b>Meta (WhatsApp Business Platform)</b>, which delivers messages between you and {NAME}.</span>,
              <span key="openai"><b>OpenAI</b>, which processes your messages, photos and voice notes to understand them and write replies. Under OpenAI’s API terms, this data isn’t used to train their models by default.</span>,
              <span key="hosting"><b>Our hosting providers</b>: Neon (database), Render (server) and Vercel (website), which store and serve your data on our behalf.</span>,
              <span key="markets"><b>Market data providers</b>: Coinbase, Yahoo Finance and mfapi.in for prices, and Alchemy and Helius for wallet balances. They receive only a stock or fund name, a currency, or a wallet address, never your phone number or other details.</span>,
              <span key="qr"><b>QR code service</b> (api.qrserver.com): when someone opens a payment link on a computer, the UPI ID and amount in that link are sent to it to draw the QR code.</span>,
            ]} />
            <p>Some of these providers may process data outside India. We may also disclose information if required by law or to protect the safety of our users.</p>
          </Section>

          <Section title="How long we keep it">
            <List items={[
              'Recent chat messages, used for conversation context, are deleted automatically after 7 days.',
              'Your ledger (transactions, budgets, goals, debts, holdings) is kept until you delete it or your account.',
              'Dashboard sign-in links expire after 15 minutes, and sessions after 30 days.',
            ]} />
          </Section>

          <Section title="Your choices and rights">
            <List items={[
              'See and download your data: open your dashboard from WhatsApp and use Export CSV.',
              'Correct something: just tell Spenzo in chat, for example “make that Uber ₹500”.',
              'Delete everything: send “delete my data” on WhatsApp and confirm. This is permanent and can’t be undone.',
              'Sign out of every browser: send “sign me out everywhere”.',
              'Stop nudges: send “stop nudges”.',
            ]} />
            <p>Under India’s Digital Personal Data Protection Act, 2023, you can also ask us for a summary of your data, ask us to correct or erase it, or raise a grievance. Write to us using the contact below.</p>
          </Section>

          <Section title="Security">
            <p>
              Data is encrypted in transit. Every request to our database is limited to the phone number it belongs to,
              messages from WhatsApp are checked to make sure they really come from Meta, and dashboard links are signed
              and short-lived. No system is perfectly secure, but we work to protect your information and will tell you
              promptly if a breach affects you.
            </p>
          </Section>

          <Section title="Not financial advice">
            <p>
              {NAME} shows facts about your own money, such as totals, budgets and portfolio values. It does not recommend
              buying or selling any investment, and nothing it says is financial, tax or legal advice.
            </p>
          </Section>

          <Section title="Children">
            <p>{NAME} is meant for people aged 18 and over. If you believe a child has given us personal data, contact us and we’ll delete it.</p>
          </Section>

          <Section title="Changes to this policy">
            <p>We may update this policy from time to time. For important changes, we’ll let you know on WhatsApp or on this website before they take effect.</p>
          </Section>

          <Section title="Contact and grievances">
            <p>
              Arav Arun, Grievance Officer · <a className="font-semibold text-leaf-deep hover:underline" href={`mailto:${CONTACT}`}>{CONTACT}</a>
              <br />We aim to reply within 7 days.
            </p>
          </Section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
