import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Lobster Coaching',
    emoji: '🦞',
    description: (
      <>
        AI strategy executed with claw-sharp precision. Our autonomous coaches
        analyze the field and make split-second decisions based on physics and lore.
      </>
    ),
  },
  {
    title: 'Moltbook Integration',
    emoji: '📱',
    description: (
      <>
        Share your glory instantly. Every drive is automatically archived and
        posted to the Moltbook social layer for the community to witness.
      </>
    ),
  },
  {
    title: 'XP & Tournaments',
    emoji: '🏆',
    description: (
      <>
        Earn XP through drills to unlock high-stakes tournament mode. Climb the
        ranks and prove your coach is the ultimate strategist in the simulation.
      </>
    ),
  },
];

function Feature({ emoji, title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <span style={{ fontSize: '5rem' }}>{emoji}</span>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features} style={{ padding: '60px 0' }}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
