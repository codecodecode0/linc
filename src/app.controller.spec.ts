import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('health', () => {
    it('should return ok status', () => {
      expect(appController.health()).toEqual({ status: 'ok', service: 'linc' });
    });
  });

  describe('stats', () => {
    it('should return platform stats', () => {
      const stats = appController.getStats();
      expect(stats).toHaveProperty('creatorsCertified');
      expect(stats).toHaveProperty('paidToCreators');
      expect(stats).toHaveProperty('avgRoas');
    });
  });

  describe('creators', () => {
    it('should return creator list', () => {
      expect(appController.getCreators().length).toBeGreaterThan(0);
    });
  });

  describe('deals', () => {
    it('should return deal list', () => {
      expect(appController.getDeals().length).toBeGreaterThan(0);
    });
  });

  describe('campaigns', () => {
    it('should return campaign list', () => {
      expect(appController.getCampaigns().length).toBeGreaterThan(0);
    });
  });

  describe('activity', () => {
    it('should return activity feed', () => {
      expect(appController.getActivity().length).toBeGreaterThan(0);
    });
  });
});
