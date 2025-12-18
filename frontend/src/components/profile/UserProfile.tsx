'use client';

import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import styles from './profile.module.css';
import { historyService } from '@/services/api';
import { HistoryRecord, VerificationStats } from '@/types/history';

export default function UserProfile() {
    const [stats, setStats] = useState<VerificationStats | null>(null);
    const [recentActivity, setRecentActivity] = useState<HistoryRecord[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    /* -------------------------
       Helpers (DO NOT TOUCH UI)
    ------------------------- */

    const isTrue = (v: any) => v === true || v === 1;

    const loadData = async () => {
        try {
            setLoading(true);
            const [statsRes, historyRes] = await Promise.all([
                historyService.getVerificationStats(),
                historyService.getRecentActivity(5)
            ]);

            setStats(statsRes.stats);
            setRecentActivity(historyRes.verifications);
        } catch (error) {
            console.error('Failed to load profile data:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatTimeAgo = (timestamp: string) => {
        const now = new Date();
        const then = new Date(timestamp);
        const diffMs = now.getTime() - then.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        return then.toLocaleDateString();
    };

    const getActivityTitle = (record: HistoryRecord) =>
        isTrue(record.is_verified) ? 'Verified' : 'Unverified';

    const getActivityDescription = (record: HistoryRecord) => {
        if (isTrue(record.is_verified)) {
            switch (record.verification_method) {
                case 'dom_text_match':
                    return 'Certificate details matched with issuer records';
                case 'qr_code':
                    return 'Certificate verified using QR code';
                case 'blockchain':
                    return 'Certificate verified on blockchain';
                case 'manual_review':
                    return 'Verified after manual review';
                case 'ai_text_match':
                    return 'Certificate content verified using AI';
                default:
                    return 'Certificate verified successfully';
            }
        }

        if (isTrue(record.is_high_risk)) {
            return 'Potential manipulation detected in the certificate';
        }

        return 'Certificate could not be verified';
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <main className={styles.mainContainer}>
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
                        <p className="mt-4 text-slate-600">Loading profile...</p>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <main className={styles.mainContainer}>

                {/* Candidate Info Block */}
                <div className={styles.candidateInfoBlock}>
                    <div className={styles.avatar}>R</div>
                    <div className={styles.candidateDetails}>
                        <div className={styles.candidateNameLarge}>Roopak Krishna</div>
                        <div className={styles.candidateDobLarge}>
                            Certificate Verification System
                        </div>
                    </div>
                </div>

                {/* Stats Grid (UNCHANGED UI) */}
                <div className={styles.statsGrid}>
                    <div className={`${styles.statCard} ${styles.cardVerified}`}>
                        <div className={styles.statLabel}>Verified</div>
                        <div className={styles.statValue}>{stats?.verified_count || 0}</div>
                    </div>

                    <div className={`${styles.statCard} ${styles.cardUnverified}`}>
                        <div className={styles.statLabel}>Unverified</div>
                        <div className={styles.statValue}>{stats?.unverified_count || 0}</div>
                    </div>

                    <div className={`${styles.statCard} ${styles.cardPending}`}>
                        <div className={styles.statLabel}>Last 24h</div>
                        <div className={styles.statValue}>{stats?.last_24h || 0}</div>
                    </div>

                    <div className={`${styles.statCard} ${styles.totalCard}`}>
                        <div className={styles.statLabel}>Total Certificates</div>
                        <div className={styles.statValue}>{stats?.total_verifications || 0}</div>
                    </div>
                </div>

                {/* Recent Activity Table (UI SAME + SERIAL NUMBERS) */}
                <div className={styles.tableContainer}>
                    <div className={styles.tableHeader}>
                        <h3 className={styles.tableTitle}>Recent User Activity Logs</h3>
                        <a href="/recent-activity" className={styles.viewAllBtn}>View All</a>
                    </div>

                    <table className={styles.table}>
                        <thead>
                            <tr className={styles.tr}>
                                <th className={styles.th}>#</th>
                                <th className={styles.th}>Activity</th>
                                <th className={`${styles.th} ${styles.colDesc}`}>Description</th>
                                <th className={styles.th} style={{ textAlign: 'right' }}>Time</th>
                            </tr>
                        </thead>

                        <tbody>
                            {recentActivity.length === 0 ? (
                                <tr className={styles.tr}>
                                    <td colSpan={4} className={styles.td} style={{ textAlign: 'center', padding: '2rem' }}>
                                        No recent activity
                                    </td>
                                </tr>
                            ) : (
                                recentActivity.map((record, index) => (
                                    <tr key={record.id} className={styles.tr}>
                                        
                                        {/* SERIAL NUMBER */}
                                        <td className={styles.td}>
                                            {index + 1}
                                        </td>

                                        <td className={`${styles.td} ${styles.colAction}`}>
                                            <div className="flex items-center gap-2">
                                                {isTrue(record.is_verified) ? (
                                                    <CheckCircle className="w-4 h-4 text-green-600 inline" />
                                                ) : (
                                                    <XCircle className="w-4 h-4 text-red-600 inline" />
                                                )}

                                                {isTrue(record.is_high_risk) && (
                                                    <AlertTriangle className="w-4 h-4 text-orange-600 inline" />
                                                )}

                                                <span>{getActivityTitle(record)}</span>
                                            </div>
                                        </td>

                                        <td className={`${styles.td} ${styles.colDesc}`}>
                                            {getActivityDescription(record)}
                                        </td>

                                        <td className={`${styles.td} ${styles.colTime}`}>
                                            {formatTimeAgo(record.timestamp)}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

            </main>
        </div>
    );
}
