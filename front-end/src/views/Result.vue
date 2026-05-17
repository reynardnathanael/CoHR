<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="card col-span-12">
            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between gap-4 flex-wrap">
                    <div>
                        <p class="text-sm uppercase tracking-[0.2em] text-indigo-500 font-semibold">Screening Result</p>
                        <h1 class="text-2xl font-bold text-slate-900">Ranked Candidates</h1>
                    </div>
                    <div class="rounded-full bg-indigo-100 text-indigo-900 px-4 py-2 font-semibold">
                        {{ totalCandidates }} candidate(s)
                    </div>
                </div>

                <p v-if="jobDescription" class="text-slate-600 whitespace-pre-line">
                    {{ jobDescription }}
                </p>

                <p v-else class="text-slate-500">
                    No analysis data found yet. Upload resumes from the upload page to generate rankings.
                </p>
            </div>
        </div>

        <div v-if="candidates.length > 0" class="col-span-12 grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div
                v-for="(candidate, index) in candidates"
                :key="candidate.file_name || index"
                class="card border border-indigo-100 shadow-sm"
            >
                <div class="flex items-start justify-between gap-4">
                    <div>
                        <p class="text-sm text-slate-500">Rank #{{ index + 1 }}</p>
                        <h2 class="text-xl font-semibold text-slate-900">{{ candidate.file_name || 'Unnamed resume' }}</h2>
                        <p class="text-sm text-slate-500 mt-1">
                            {{ candidate.email || 'Email not found' }}
                            <span v-if="candidate.phone_number"> · {{ candidate.phone_number }}</span>
                        </p>
                        <p class="text-sm text-slate-500">
                            {{ candidate.location || 'Location not extracted' }}
                        </p>
                    </div>

                    <div class="rounded-2xl bg-indigo-50 px-4 py-3 text-right min-w-28">
                        <p class="text-xs uppercase tracking-[0.2em] text-indigo-500 font-semibold">Match</p>
                        <p class="text-3xl font-bold text-indigo-900">{{ candidate.similarity_score }}%</p>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-3 mt-5">
                    <div class="rounded-xl bg-slate-50 p-3">
                        <p class="text-xs text-slate-500">Embedding</p>
                        <p class="text-lg font-semibold text-slate-900">{{ candidate.embedding_score ?? 0 }}%</p>
                    </div>
                    <div class="rounded-xl bg-slate-50 p-3">
                        <p class="text-xs text-slate-500">Skills</p>
                        <p class="text-lg font-semibold text-slate-900">{{ candidate.skill_score ?? 0 }}%</p>
                    </div>
                    <div class="rounded-xl bg-slate-50 p-3">
                        <p class="text-xs text-slate-500">Matched</p>
                        <p class="text-lg font-semibold text-slate-900">{{ candidate.matched_skills?.length || 0 }}</p>
                    </div>
                </div>

                <div class="mt-5">
                    <p class="text-sm font-semibold text-slate-700 mb-2">Matched Skills</p>
                    <div class="flex flex-wrap gap-2">
                        <span
                            v-for="skill in candidate.matched_skills || []"
                            :key="skill"
                            class="rounded-full bg-indigo-100 text-indigo-900 px-3 py-1 text-xs font-medium"
                        >
                            {{ skill }}
                        </span>
                        <span v-if="!candidate.matched_skills || candidate.matched_skills.length === 0" class="text-sm text-slate-500">
                            No direct skill overlap detected.
                        </span>
                    </div>
                </div>

                <div class="mt-5 space-y-4">
                    <div>
                        <p class="text-sm font-semibold text-slate-700 mb-1">Summary</p>
                        <p class="text-sm text-slate-600 line-clamp-4">{{ candidate.summary || 'No summary extracted.' }}</p>
                    </div>
                    <div>
                        <p class="text-sm font-semibold text-slate-700 mb-1">Education</p>
                        <p class="text-sm text-slate-600 line-clamp-4">{{ candidate.education || 'No education extracted.' }}</p>
                    </div>
                    <div>
                        <p class="text-sm font-semibold text-slate-700 mb-1">Experience</p>
                        <p class="text-sm text-slate-600 line-clamp-6">{{ candidate.experience || 'No experience extracted.' }}</p>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="card col-span-12">
            <p class="text-slate-600">There are no ranked candidates to display yet.</p>
        </div>

        <div v-if="failedFiles.length > 0" class="card col-span-12">
            <h2 class="text-lg font-semibold text-slate-900 mb-3">Failed Files</h2>
            <ul class="space-y-2">
                <li v-for="item in failedFiles" :key="item.file_name" class="text-sm text-slate-600">
                    <span class="font-medium text-slate-900">{{ item.file_name }}</span>
                    <span> - {{ item.error }}</span>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const analysis = ref(null);

const loadAnalysis = () => {
    const stored = sessionStorage.getItem('cohr_analysis_result');

    if (!stored) {
        analysis.value = null;
        return;
    }

    try {
        analysis.value = JSON.parse(stored);
    } catch (error) {
        console.error('Failed to parse analysis result:', error);
        analysis.value = null;
    }
};

loadAnalysis();

const candidates = computed(() => analysis.value?.candidates || []);
const failedFiles = computed(() => analysis.value?.failed_files || []);
const jobDescription = computed(() => analysis.value?.job_description || '');
const totalCandidates = computed(() => analysis.value?.total || candidates.value.length || 0);
</script>
