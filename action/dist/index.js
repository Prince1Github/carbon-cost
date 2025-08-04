"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const core = __importStar(require("@actions/core"));
const github = __importStar(require("@actions/github"));
const axios_1 = __importDefault(require("axios"));
/**
 * Estimates CO2 emissions based on job duration and machine type
 * @param duration - Job duration in seconds
 * @param machineType - Type of GitHub Actions runner
 * @returns Estimated CO2 emissions in kg
 */
function estimateCO2(duration, machineType) {
    const factors = {
        'ubuntu-latest': 0.0002,
        'windows-latest': 0.0003,
        'macos-latest': 0.00025,
    };
    return duration * (factors[machineType] || 0.0002);
}
/**
 * Determines badge color based on CO2 emission threshold
 * @param co2 - CO2 emission in kg
 * @returns Badge information with label and color
 */
function getBadgeColor(co2) {
    if (co2 < 0.5)
        return { label: 'Green', color: 'brightgreen' };
    if (co2 < 1.5)
        return { label: 'Yellow', color: 'yellow' };
    return { label: 'Red', color: 'red' };
}
/**
 * Main function that runs the Carbon-Cost GitHub Action
 */
async function run() {
    try {
        const backendUrl = core.getInput('backend_url', { required: true });
        // Generate mock job duration (1-10 minutes in seconds)
        const duration = Math.floor(Math.random() * 600) + 60;
        const machineType = process.env['RUNNER_OS']?.toLowerCase() || 'ubuntu-latest';
        // Calculate CO2 emissions and badge
        const co2 = estimateCO2(duration, machineType);
        const badge = getBadgeColor(co2);
        const badgeUrl = `https://img.shields.io/badge/CO2-${badge.label}-${badge.color}`;
        // Prepare emission data
        const emissionData = {
            repo: github.context.repo.repo,
            owner: github.context.repo.owner,
            run_id: github.context.runId.toString(),
            co2,
            duration,
            machine_type: machineType,
            badge: badge.label,
            timestamp: new Date().toISOString(),
        };
        // Send data to backend API
        const response = await axios_1.default.post(backendUrl, emissionData);
        if (response.status !== 201) {
            throw new Error(`Failed to record emission data: ${response.status}`);
        }
        // Set action outputs
        core.setOutput('co2', co2.toFixed(3));
        core.setOutput('badge_url', badgeUrl);
        // Log results
        core.notice(`CO2: ${co2.toFixed(3)} kg, Badge: ${badge.label}`);
        core.notice(`Badge URL: ${badgeUrl}`);
    }
    catch (error) {
        core.setFailed(`Action failed: ${error.message}`);
    }
}
// Execute the action
run();
