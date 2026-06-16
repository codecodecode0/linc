import { clamp, compactNumber, titleCase } from '../shared/format.js';

const CREATOR_AUDIENCE = {
  'Beauty & Skincare': {
    audience: 'Women 18-34, metros, premium grooming',
    demo: '72% women · 18-34',
    cities: 'Mumbai, Delhi, Pune',
  },
  'Food & Drinks': {
    audience: 'Urban food explorers, students, young families',
    demo: '58% men · 18-34',
    cities: 'Delhi, Mumbai, Jaipur',
  },
  'Health & Fitness': {
    audience: 'Wellness buyers, active professionals, gym communities',
    demo: '54% women · 22-38',
    cities: 'Bengaluru, Hyderabad, Pune',
  },
  'Phones & Gadgets': {
    audience: 'Tech shoppers, gamers, early adopters',
    demo: '68% men · 18-30',
    cities: 'Hyderabad, Bengaluru, Chennai',
  },
};

function parseFollowers(label) {
  const raw = String(label || '').trim().toUpperCase();
  const n = Number(raw.replace(/[^0-9.]/g, '')) || 0;
  if (raw.includes('CR')) return n * 10000000;
  if (raw.includes('M')) return n * 1000000;
  if (raw.includes('L')) return n * 100000;
  if (raw.includes('K')) return n * 1000;
  return n;
}

function parsePercent(label) {
  return Number(String(label || '').replace('%', '')) || 0;
}

function categoryScore(category, niche) {
  const haystack = `${category || ''} ${niche || ''}`.toLowerCase();
  const pairs = [
    ['beauty', ['beauty', 'skin', 'hair', 'wellness']],
    ['skincare', ['beauty', 'skin', 'wellness']],
    ['food', ['food', 'drink', 'fitness']],
    ['fitness', ['health', 'fitness', 'wellness']],
    ['tech', ['tech', 'phone', 'gadget']],
    ['saas', ['tech', 'business']],
    ['fashion', ['beauty', 'lifestyle']],
  ];
  const matched = pairs.find(([needle]) => haystack.includes(needle));
  if (!matched) return 18;
  return matched[1].some((word) => String(niche || '').toLowerCase().includes(word)) ? 30 : 14;
}

function objectiveType(objective) {
  if (objective === 'conversions') return 'real_video';
  if (objective === 'traffic' || objective === 'app_installs') return 'ai_video';
  if (objective === 'awareness') return 'ai_static';
  return 'real_video';
}

export function recommendationPlan(campaign, creators, brand = {}) {
  const category = campaign.productCategory || brand.category || '';
  const budget = Number(campaign.budgetAmount || 0);
  const objective = campaign.objective || 'awareness';
  const scored = creators
    .map((creator) => {
      const followers = parseFollowers(creator.followers);
      const engagement = parsePercent(creator.engagement);
      const rate = Number(creator.rate || 45000);
      const audience = CREATOR_AUDIENCE[creator.niche] || {
        audience: 'Broad creator audience with mixed metro reach',
        demo: '18-34 core',
        cities: creator.city || 'India',
      };
      const efficiency = rate ? (followers * Math.max(engagement, 1)) / rate : 0;
      const score = Math.round(
        categoryScore(category, creator.niche) +
          clamp(engagement * 7, 8, 34) +
          clamp(efficiency / 240, 4, 18) +
          (creator.certified ? 8 : 0) +
          clamp((creator.matchScore || 70) / 12, 4, 9),
      );
      return { creator, audience, followers, engagement, rate, score: clamp(score, 45, 97) };
    })
    .sort((a, b) => b.score - a.score);

  const targetCount = budget >= 250000 ? 3 : budget >= 120000 ? 2 : 1;
  const picked = scored.slice(0, targetCount);
  const scoreTotal = picked.reduce((sum, p) => sum + p.score, 0) || 1;
  let remaining = budget;

  return picked.map((item, index) => {
    const proportional = Math.round((budget * item.score) / scoreTotal / 5000) * 5000;
    const minQuote = Math.round(item.rate * 0.75 / 5000) * 5000;
    const quote = index === picked.length - 1
      ? Math.max(minQuote, remaining)
      : clamp(proportional, minQuote, Math.round(item.rate * 1.35 / 5000) * 5000);
    remaining -= quote;
    const videos = Math.max(1, Math.round(quote / Math.max(item.rate * 0.85, 1)));
    const type = objectiveType(objective);
    return {
      ...item,
      quote,
      videos,
      type,
      rationale: [
        `${item.score}% fit for ${titleCase(objective)}`,
        `${item.audience.demo}`,
        `${compactNumber(item.followers)} followers at ${item.engagement}% engagement`,
      ],
    };
  });
}

