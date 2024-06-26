/* generated using openapi-typescript-codegen -- do no edit */

/* istanbul ignore file */

/* tslint:disable */

/* eslint-disable */
import type { AgentDeployment } from './AgentDeployment';
import type { AgentModel } from './AgentModel';

export type Agent = {
  user_id: string;
  id: string;
  created_at: string;
  updated_at: string;
  version: number;
  name: string;
  description: string | null;
  preamble: string | null;
  temperature: number;
  model: AgentModel;
  deployment: AgentDeployment;
};
