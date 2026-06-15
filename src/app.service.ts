import { Injectable } from '@nestjs/common';

export interface Creator {
  id: string;
  name: string;
  handle: string;
  niche: string;
  location: string;
  followers: string;
  engagement: string;
  matchScore: number;
  avatar: string;
  certified: boolean;
  rate: number; // starting rate per video, in rupees
}

export interface Deal {
  id: string;
  title: string;
  brand: string;
  creator: string;
  status: 'brief' | 'contract' | 'filming' | 'review' | 'paid';
  budget: number; // rupees
  path: 'video' | 'ai-static' | 'ai-video';
}

export interface Campaign {
  id: string;
  name: string;
  brand: string;
  creator: string;
  status: 'live' | 'draft' | 'ended';
  spend: number; // rupees
  roas: number; // return on ad spend, e.g. 4.8x
  ctr: number; // click-through rate %
  reach: number; // people reached
}

export interface Activity {
  id: string;
  type: 'earning' | 'match' | 'delivery' | 'campaign';
  text: string;
  meta: string;
  time: string;
}

export interface PlatformStats {
  creatorsCertified: number;
  brandsActive: number;
  agenciesActive: number;
  aiAdsGenerated: number;
  paidToCreators: number; // rupees
  avgRoas: number;
}

@Injectable()
export class AppService {
  getStats(): PlatformStats {
    return {
      creatorsCertified: 9000,
      brandsActive: 1200,
      agenciesActive: 180,
      aiAdsGenerated: 184000,
      // Total paid out to creators, in rupees (shown as ₹24Cr)
      paidToCreators: 240000000,
      avgRoas: 5.3,
    };
  }

  getCreators(): Creator[] {
    return [
      {
        id: '1',
        name: 'Maya Chen',
        handle: '@mayacreates',
        niche: 'Beauty & Skincare',
        location: 'Mumbai',
        followers: '480K',
        engagement: '4.8%',
        matchScore: 96,
        avatar: 'MC',
        certified: true,
        rate: 85000,
      },
      {
        id: '2',
        name: 'Rohan Mehta',
        handle: '@rohaneats',
        niche: 'Food & Drinks',
        location: 'Delhi',
        followers: '320K',
        engagement: '3.2%',
        matchScore: 91,
        avatar: 'RM',
        certified: true,
        rate: 60000,
      },
      {
        id: '3',
        name: 'Priya Sharma',
        handle: '@priyafit',
        niche: 'Health & Fitness',
        location: 'Bengaluru',
        followers: '610K',
        engagement: '5.1%',
        matchScore: 88,
        avatar: 'PS',
        certified: false,
        rate: 95000,
      },
      {
        id: '4',
        name: 'Arjun Nair',
        handle: '@arjuntech',
        niche: 'Phones & Gadgets',
        location: 'Hyderabad',
        followers: '270K',
        engagement: '2.9%',
        matchScore: 84,
        avatar: 'AN',
        certified: true,
        rate: 70000,
      },
    ];
  }

  getDeals(): Deal[] {
    // Budgets are in rupees
    return [
      {
        id: 'd1',
        title: 'Glow Face Serum — Video Ad',
        brand: 'Glow Labs',
        creator: 'Maya Chen',
        status: 'review',
        budget: 85000,
        path: 'video',
      },
      {
        id: 'd2',
        title: 'Protein Bar — AI Photo Ads',
        brand: 'Fuel Co',
        creator: 'Rohan Mehta',
        status: 'paid',
        budget: 55000,
        path: 'ai-static',
      },
      {
        id: 'd3',
        title: 'Smart Watch — AI Video Ads',
        brand: 'Pulse Gear',
        creator: 'Arjun Nair',
        status: 'filming',
        budget: 160000,
        path: 'ai-video',
      },
      {
        id: 'd4',
        title: 'Yoga Mat — New Deal',
        brand: 'ZenFlow',
        creator: 'Priya Sharma',
        status: 'contract',
        budget: 70000,
        path: 'video',
      },
    ];
  }

  getCampaigns(): Campaign[] {
    // Spend is in rupees
    return [
      {
        id: 'c1',
        name: 'Glow Serum — Festive Push',
        brand: 'Glow Labs',
        creator: 'Maya Chen',
        status: 'live',
        spend: 420000,
        roas: 6.4,
        ctr: 2.8,
        reach: 1840000,
      },
      {
        id: 'c2',
        name: 'Protein Bar — Always On',
        brand: 'Fuel Co',
        creator: 'Rohan Mehta',
        status: 'live',
        spend: 280000,
        roas: 4.9,
        ctr: 2.1,
        reach: 1120000,
      },
      {
        id: 'c3',
        name: 'Smart Watch — Launch',
        brand: 'Pulse Gear',
        creator: 'Arjun Nair',
        status: 'live',
        spend: 650000,
        roas: 5.7,
        ctr: 3.2,
        reach: 2350000,
      },
      {
        id: 'c4',
        name: 'Yoga Mat — Test Batch',
        brand: 'ZenFlow',
        creator: 'Priya Sharma',
        status: 'draft',
        spend: 0,
        roas: 0,
        ctr: 0,
        reach: 0,
      },
    ];
  }

  getActivity(): Activity[] {
    return [
      {
        id: 'a1',
        type: 'earning',
        text: 'Maya Chen earned ₹900',
        meta: 'Glow Labs used her look in an AI ad',
        time: 'just now',
      },
      {
        id: 'a2',
        type: 'campaign',
        text: 'Smart Watch campaign hit 5.7x return',
        meta: 'Pulse Gear · live now',
        time: '2 min ago',
      },
      {
        id: 'a3',
        type: 'match',
        text: 'Fuel Co matched with Rohan Mehta',
        meta: '91% fit · suggested by linc',
        time: '6 min ago',
      },
      {
        id: 'a4',
        type: 'delivery',
        text: 'Glow Face Serum video delivered',
        meta: 'Waiting for brand to check',
        time: '14 min ago',
      },
      {
        id: 'a5',
        type: 'earning',
        text: 'Arjun Nair earned ₹1,200',
        meta: 'Pulse Gear used his look in an AI ad',
        time: '21 min ago',
      },
    ];
  }
}
