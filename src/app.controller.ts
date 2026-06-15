import { Controller, Get, Res } from '@nestjs/common';
import type { Response } from 'express';
import { join } from 'path';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('health')
  health() {
    return { status: 'ok', service: 'linc' };
  }

  @Get('stats')
  getStats() {
    return this.appService.getStats();
  }

  @Get('creators')
  getCreators() {
    return this.appService.getCreators();
  }

  @Get('deals')
  getDeals() {
    return this.appService.getDeals();
  }

  @Get('campaigns')
  getCampaigns() {
    return this.appService.getCampaigns();
  }

  @Get('activity')
  getActivity() {
    return this.appService.getActivity();
  }

  @Get()
  serveApp(@Res() res: Response) {
    res.sendFile(join(__dirname, '..', 'public', 'index.html'));
  }
}
