import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { App } from 'supertest/types';
import { AppModule } from './../src/app.module';

describe('AppController (e2e)', () => {
  let app: INestApplication<App>;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('api', { exclude: ['/', 'health'] });
    await app.init();
  });

  afterEach(async () => {
    await app.close();
  });

  it('/health (GET)', () => {
    return request(app.getHttpServer())
      .get('/health')
      .expect(200)
      .expect({ status: 'ok', service: 'linc' });
  });

  it('/api/stats (GET)', () => {
    return request(app.getHttpServer())
      .get('/api/stats')
      .expect(200)
      .expect((res) => {
        const body = res.body as { creatorsCertified: number };
        expect(body.creatorsCertified).toBeDefined();
      });
  });

  it('/api/creators (GET)', () => {
    return request(app.getHttpServer())
      .get('/api/creators')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body)).toBe(true);
      });
  });

  it('/api/deals (GET)', () => {
    return request(app.getHttpServer())
      .get('/api/deals')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body)).toBe(true);
      });
  });
});
