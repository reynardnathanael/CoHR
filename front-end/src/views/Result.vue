<template>
  <div class="grid grid-cols-12 gap-8">
    <div class="card col-span-12">
      <div class="flex flex-col gap-4">
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p
              class="text-sm uppercase tracking-[0.2em] text-indigo-500 font-semibold"
            >
              Screening Result
            </p>
            <h1 class="text-2xl font-bold text-slate-900">Ranked Candidates</h1>
          </div>
          <div
            class="rounded-full bg-indigo-100 text-indigo-900 px-4 py-2 font-semibold"
          >
            {{ totalCandidates }} candidate(s)
          </div>
        </div>

        <p v-if="jobDescription" class="text-slate-600 whitespace-pre-line">
          {{ jobDescription }}
        </p>

        <p v-else class="text-slate-500">
          No analysis data found yet. Upload resumes from the upload page to
          generate rankings.
        </p>
      </div>
    </div>

    <div
      v-if="candidates.length > 0"
      class="col-span-12 grid grid-cols-1 xl:grid-cols-2 gap-6"
    >
      <div
        v-for="(candidate, index) in candidates"
        :key="candidate.file_name || index"
        class="card border border-indigo-100 shadow-sm"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm text-slate-500">Rank #{{ index + 1 }}</p>
            <h2 class="text-xl font-semibold text-slate-900">
              {{ candidate.name || candidate.file_name?.replace(/\.pdf$/i, '') || "Unnamed Candidate" }}
            </h2>
            <p class="text-xs text-indigo-500 font-medium mt-1 flex items-center gap-1">
              <i class="pi pi-file-pdf"></i> {{ candidate.file_name }}
            </p>
            <p class="text-sm text-slate-500 mt-1">
              {{ candidate.email || "Email not found" }}
              <span v-if="candidate.phone_number">
                · {{ candidate.phone_number }}</span
              >
            </p>
            <p class="text-sm text-slate-500">
              {{ candidate.location || "Location not extracted" }}
            </p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
              >
                Location: {{ candidate.location || "Not found" }}
              </span>
              <span
                class="rounded-full bg-indigo-100 px-3 py-1 text-xs font-medium text-indigo-900"
              >
                Skills: {{ candidate.matched_skills.length }} matched
              </span>
            </div>
          </div>

          <div class="rounded-2xl bg-indigo-50 px-4 py-3 text-right min-w-28">
            <p
              class="text-xs uppercase tracking-[0.2em] text-indigo-500 font-semibold"
            >
              Match
            </p>
            <p class="text-3xl font-bold text-indigo-900">
              {{ candidate.similarity_score }}%
            </p>
          </div>
        </div>

        <div class="mt-5">
          <p class="text-sm font-semibold text-slate-700 mb-2">
            Matched Skills
          </p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="skill in candidate.matched_skills"
              :key="skill"
              class="rounded-full bg-indigo-100 text-indigo-900 px-3 py-1 text-xs font-medium"
            >
              {{ skill }}
            </span>
            <span
              v-if="candidate.matched_skills.length === 0"
              class="text-sm text-slate-500"
            >
              No direct skill overlap detected.
            </span>
          </div>
        </div>

        <div class="mt-5">
          <p class="text-sm font-semibold text-slate-700 mb-2">
            Extracted Skills
          </p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="skill in candidate.extracted_skills"
              :key="skill"
              class="rounded-full bg-emerald-100 text-emerald-900 px-3 py-1 text-xs font-medium"
            >
              {{ skill }}
            </span>
            <span
              v-if="candidate.extracted_skills.length === 0"
              class="text-sm text-slate-500"
            >
              No skills were extracted from this resume.
            </span>
          </div>
        </div>

        <div class="mt-5 space-y-4">
          <div>
            <p class="text-sm font-semibold text-slate-700 mb-1">Summary</p>
            <div
              v-if="candidate.summaryLoading"
              class="flex items-center gap-2 text-indigo-400 text-sm py-1"
            >
              <i class="pi pi-spin pi-spinner"></i> Generating AI summary...
            </div>
            <div v-else class="text-sm text-slate-600 max-h-32 overflow-y-auto pr-3 whitespace-pre-line text-justify">
              {{
                candidate.ai_summary ||
                candidate.summary ||
                "No summary extracted."
              }}
            </div>
          </div>
          
          <!-- Education Section -->
          <div>
            <p class="text-sm font-semibold text-slate-700 mb-2">Education</p>
            <div v-if="candidate.llm_resume?.education" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Bachelor</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.llm_resume?.education?.bachelor_edu) || "No bachelor education extracted." }}
                </p>
              </div>
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Master</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.llm_resume?.education?.master_edu) || "No master education extracted." }}
                </p>
              </div>
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">PhD</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.llm_resume?.education?.phd_edu) || "No PhD education extracted." }}
                </p>
              </div>
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Other</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.llm_resume?.education?.other_edu) || "No additional education extracted." }}
                </p>
              </div>
            </div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Bachelor</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.education?.bachelor_edu) || "No bachelor education extracted." }}
                </p>
              </div>
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Master</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.education?.master_edu) || "No master education extracted." }}
                </p>
              </div>
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">PhD</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.education?.phd_edu) || "No PhD education extracted." }}
                </p>
              </div>
              <div class="rounded-xl bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">Other</p>
                <p class="text-sm text-slate-600 whitespace-pre-line">
                  {{ formatEducationBucket(candidate.education?.other_edu) || "No additional education extracted." }}
                </p>
              </div>
            </div>
          </div>

          <!-- Experience Section -->
          <div>
            <p class="text-sm font-semibold text-slate-700 mb-1">Experience</p>
            <div
              v-if="
                Array.isArray(candidate.experience) &&
                candidate.experience.length
              "
              class="max-h-60 overflow-y-auto pr-3"
            >
              <div
                v-for="(item, idx) in candidate.experience"
                :key="idx"
                class="mb-4 border-b border-slate-100 pb-4 last:border-0 last:pb-0 last:mb-0"
              >
                <div v-if="typeof item === 'string'" class="text-sm text-slate-600 whitespace-pre-line text-justify">
                  {{ item }}
                </div>
                <div v-else>
                  <div class="flex justify-between items-start mb-1">
                    <span class="font-semibold text-slate-800 text-sm">{{ item.experience_title || item.title || item.role || "Unknown Role" }}</span>
                    <span class="text-xs text-slate-500 whitespace-nowrap ml-3">{{ item.experience_date || item.dates || item.start_date || "" }}</span>
                  </div>
                  <p class="text-xs font-medium text-indigo-600 mb-1">{{ item.company || item.institution || item.organization || "" }}</p>
                  <p class="text-sm text-slate-600 whitespace-pre-line text-justify">{{ item.experience_description || item.description || item.summary || "" }}</p>
                </div>
              </div>
            </div>
            <p
              v-else-if="
                candidate.experience && typeof candidate.experience === 'string'
              "
              class="max-h-60 overflow-y-auto pr-3 text-sm text-slate-600 whitespace-pre-line text-justify"
            >
              {{ candidate.experience }}
            </p>
            <p v-else class="text-sm text-slate-600">
              No experience extracted.
            </p>
          </div>

          <!-- Projects Section -->
          <div>
            <p class="text-sm font-semibold text-slate-700 mb-1">Projects</p>
            <div
              v-if="
                Array.isArray(candidate.projects) && candidate.projects.length
              "
              class="max-h-60 overflow-y-auto pr-3"
            >
              <div
                v-for="(item, idx) in candidate.projects"
                :key="idx"
                class="mb-4 border-b border-slate-100 pb-4 last:border-0 last:pb-0 last:mb-0"
              >
                <div v-if="typeof item === 'string'" class="text-sm text-slate-600 whitespace-pre-line text-justify">
                  {{ item }}
                </div>
                <div v-else>
                  <div class="flex justify-between items-start mb-1">
                    <span class="font-semibold text-slate-800 text-sm">{{ item.project_title || item.name || item.title || "Unnamed Project" }}</span>
                    <span class="text-xs text-slate-500 whitespace-nowrap ml-3">{{ item.project_date || item.dates || item.start_date || "" }}</span>
                  </div>
                  <p class="text-sm text-slate-600 whitespace-pre-line text-justify">{{ item.project_desc || item.description || item.summary || "" }}</p>
                  <p v-if="item.technologies && item.technologies.length" class="text-xs text-slate-500 mt-2">
                    <span class="font-medium text-slate-700">Tech:</span> {{ Array.isArray(item.technologies) ? item.technologies.join(', ') : item.technologies }}
                  </p>
                </div>
              </div>
            </div>
            <p
              v-else-if="
                candidate.projects && typeof candidate.projects === 'string'
              "
              class="max-h-60 overflow-y-auto pr-3 text-sm text-slate-600 whitespace-pre-line text-justify"
            >
              {{ candidate.projects }}
            </p>
            <p v-else class="text-sm text-slate-600">No projects extracted.</p>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-700 mb-1">
              Certifications
            </p>
            <div
              v-if="
                Array.isArray(candidate.certifications) &&
                candidate.certifications.length
              "
            >
              <ul class="list-disc pl-4">
                <li
                  v-for="(item, idx) in candidate.certifications"
                  :key="idx"
                  class="text-sm text-slate-600 line-clamp-3"
                >
                  {{ typeof item === "string" ? item : formatObject(item) }}
                </li>
              </ul>
            </div>
            <p
              v-else-if="
                candidate.certifications &&
                typeof candidate.certifications === 'string'
              "
              class="text-sm text-slate-600 whitespace-pre-line line-clamp-4"
            >
              {{ candidate.certifications }}
            </p>
            <p v-else class="text-sm text-slate-600">
              No certifications extracted.
            </p>
          </div>
          <div
            v-if="candidate.achievements && candidate.achievements.length > 0"
          >
            <p class="text-sm font-semibold text-slate-700 mb-1">
              Achievements
            </p>
            <div v-if="Array.isArray(candidate.achievements)">
              <ul class="list-disc pl-4">
                <li
                  v-for="(item, idx) in candidate.achievements"
                  :key="idx"
                  class="text-sm text-slate-600"
                >
                  {{ typeof item === "string" ? item : formatObject(item) }}
                </li>
              </ul>
            </div>
            <p v-else class="text-sm text-slate-600">
              {{ candidate.achievements }}
            </p>
          </div>
          <div v-if="candidate.languages && candidate.languages.length > 0">
            <p class="text-sm font-semibold text-slate-700 mb-1">Languages</p>
            <div v-if="Array.isArray(candidate.languages)">
              <ul class="list-disc pl-4">
                <li
                  v-for="(item, idx) in candidate.languages"
                  :key="idx"
                  class="text-sm text-slate-600"
                >
                  {{ typeof item === "string" ? item : formatObject(item) }}
                </li>
              </ul>
            </div>
            <p v-else class="text-sm text-slate-600">
              {{ candidate.languages }}
            </p>
          </div>
        </div>

        <!-- AI AGENT PROGRESSIVE RENDERING SECTION -->
        <div
          class="mt-6 rounded-2xl bg-indigo-50/50 border border-indigo-100 p-5 relative overflow-hidden"
        >
          <h3
            class="text-base font-bold text-indigo-900 mb-4 flex items-center gap-2"
          >
            <i class="pi pi-sparkles text-indigo-500"></i> AI Agent Evaluation
            (ARIA)
          </h3>

          <!-- Loading State -->
          <div
            v-if="candidate.agentLoading"
            class="flex flex-col items-center justify-center py-6 text-indigo-400"
          >
            <i class="pi pi-spin pi-spinner text-4xl mb-3"></i>
            <p class="text-sm font-medium animate-pulse">
              ARIA is analyzing candidate fit...
            </p>
          </div>

          <!-- Result State -->
          <div
            v-else-if="candidate.screening && !candidate.screening.error"
            class="space-y-4"
          >
            <div class="flex justify-between items-center">
              <span
                :class="{
                  'bg-emerald-100 text-emerald-800':
                    candidate.screening.fit_category === 'Strong Fit',
                  'bg-amber-100 text-amber-800':
                    candidate.screening.fit_category === 'Potential Fit',
                  'bg-red-100 text-red-800':
                    candidate.screening.fit_category === 'Weak Fit',
                }"
                class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
              >
                {{ candidate.screening.fit_category }}
              </span>
              <span class="text-sm font-bold text-slate-700">
                Confidence: {{ candidate.screening.score }}%
              </span>
            </div>

            <div class="grid grid-cols-1 gap-4">
              <div>
                <p class="text-xs font-bold text-slate-500 uppercase mb-2">
                  Strengths & Weaknesses
                </p>
                <ul
                  class="list-disc pl-4 text-sm text-slate-700 space-y-1 mb-2"
                >
                  <li
                    v-for="s in candidate.screening.strengths"
                    :key="s"
                    class="text-emerald-700"
                  >
                    {{ s }}
                  </li>
                  <li
                    v-for="w in candidate.screening.weaknesses"
                    :key="w"
                    class="text-red-700"
                  >
                    {{ w }}
                  </li>
                </ul>
                <p class="text-sm mt-3 pt-3 border-t border-indigo-100">
                  <span class="font-bold text-slate-700">Recommendation:</span>
                  <span class="text-slate-600 ml-2">{{
                    candidate.screening.recommendation
                  }}</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Error State -->
          <div v-else class="text-sm text-red-500 font-medium">
            {{
              candidate.screening?.error ||
              "Failed to load AI evaluation. Ensure Ollama is running."
            }}
          </div>
        </div>
      </div>
    </div>

    <div v-else class="card col-span-12">
      <p class="text-slate-600">
        There are no ranked candidates to display yet.
      </p>
    </div>

    <div v-if="failedFiles.length > 0" class="card col-span-12">
      <h2 class="text-lg font-semibold text-slate-900 mb-3">Failed Files</h2>
      <ul class="space-y-2">
        <li
          v-for="item in failedFiles"
          :key="item.file_name"
          class="text-sm text-slate-600"
        >
          <span class="font-medium text-slate-900">{{ item.file_name }}</span>
          <span> - {{ item.error }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { api } from "../helpers/axios";

const analysis = ref(null);
const candidates = ref([]);
const jobProfile = computed(() => analysis.value?.job_profile || {});

const loadAnalysis = () => {
  const stored = sessionStorage.getItem("cohr_analysis_result");

  if (!stored) {
    analysis.value = null;
    candidates.value = [];
    // Try to fetch the latest analysis from the backend if available
    fetchLatestAnalysis();
    return;
  }

  try {
    analysis.value = JSON.parse(stored);
    candidates.value = (analysis.value?.candidates || []).map((c) => ({
      ...normalizeCandidate(c),
      agentLoading: !c.screening, // Set loading state to true if no screening exists yet
      summaryLoading: !c.ai_summary,
    }));
  } catch (error) {
    console.error("Failed to parse analysis result:", error);
    analysis.value = null;
  }
};

const fetchLatestAnalysis = async () => {
  try {
    const response = await api.get("/latest-analysis");
    if (response && response.data) {
      const payload = response.data;
      payload.job_description =
        payload.job_profile && payload.job_profile.job_description
          ? payload.job_profile.job_description
          : jobDescription.value || "";
      sessionStorage.setItem("cohr_analysis_result", JSON.stringify(payload));
      analysis.value = payload;
      candidates.value = (analysis.value?.candidates || []).map((c) => ({
        ...normalizeCandidate(c),
        agentLoading: !c.screening,
        summaryLoading: !c.ai_summary,
      }));
    }
  } catch (err) {
    // Ignore if backend doesn't have uploaded analysis
    // console.debug('No uploaded analysis available:', err?.response?.status);
  }
};

const normalizeSkills = (value) => {
  if (Array.isArray(value)) {
    return value.filter(Boolean);
  }

  if (typeof value === "string" && value.trim()) {
    return [value.trim()];
  }

  return [];
};

const normalizeList = (value) => {
  if (Array.isArray(value)) {
    return value
      .filter(Boolean)
      .map((entry) => String(entry).trim())
      .filter(Boolean);
  }

  if (typeof value === "string" && value.trim()) {
    return [value.trim()];
  }

  return [];
};

const formatEducationBucket = (value) => {
  if (!value) return "";
  const arr = Array.isArray(value) ? value : [value];

  return arr
    .filter(Boolean)
    .map((entry) => {
      if (typeof entry === "string") return entry.trim();

      // Extract both the university and the degree based on the schema keys
      const uni = entry.university || entry.institution || entry.bachelor_university || entry.master_university || entry.phd_university || entry.other_text || "";
      const deg = entry.degree || entry.bachelor_degree || entry.master_degree || entry.phd_degree || entry.other_degree || "";
      
      if (uni && deg) return `${deg.trim()} - ${uni.trim()}`;
      if (deg) return deg.trim();
      if (uni) return uni.trim();
      
      if (entry.raw_text) return entry.raw_text.trim();
      return formatObject(entry);
    })
    .filter(Boolean)
    .join("\n\n");
};

const formatLocation = (value) => {
  if (!value) {
    return "";
  }

  if (typeof value === "string") {
    return value.trim();
  }

  if (Array.isArray(value)) {
    return value
      .map((entry) => formatLocation(entry))
      .filter(Boolean)
      .join(", ");
  }

  if (typeof value === "object") {
    const parts = [
      value.location,
      value.city,
      value.state,
      value.region,
      value.country,
      value.name,
    ].filter((part) => typeof part === "string" && part.trim());

    return parts.join(", ");
  }

  return "";
};

const formatObject = (value) => {
  if (!value && value !== 0) return "";
  if (typeof value === "string") return value;
  try {
    if (Array.isArray(value))
      return value
        .map((v) => (typeof v === "string" ? v : JSON.stringify(v)))
        .join(", ");
    if (typeof value === "object") {
      // Try to build a readable string from common fields
      const parts = [];
      for (const k of [
        "degree",
        "title",
        "experience_title",
        "project_title",
        "name",
        "role",
        "university",
        "institution",
        "company",
        "organization",
        "description",
        "experience_description",
        "project_desc",
        "summary",
        "responsibilities",
        "steps"
      ]) {
        if (value[k]) {
          parts.push(Array.isArray(value[k]) ? value[k].join(", ") : value[k]);
        }
      }
      if (parts.length) return parts.join(" — ");
      return JSON.stringify(value);
    }
    return String(value);
  } catch (e) {
    return String(value);
  }
};

const normalizeCandidate = (candidate) => ({
  ...candidate,
  location: formatLocation(
    candidate?.location ||
      candidate?.extracted_location ||
      candidate?.contact?.location ||
      candidate?.contact?.city ||
      candidate?.city ||
      candidate?.country,
  ),
  matched_skills: normalizeSkills(candidate?.matched_skills),
  extracted_skills: normalizeSkills(candidate?.extracted_skills),
  education: {
    bachelor_edu: candidate?.education?.bachelor_edu || [],
    master_edu: candidate?.education?.master_edu || [],
    phd_edu: candidate?.education?.phd_edu || [],
    other_edu: candidate?.education?.other_edu || candidate?.education || [],
  },
});

const failedFiles = computed(() => analysis.value?.failed_files || []);
const jobDescription = computed(() => analysis.value?.job_description || "");
const totalCandidates = computed(
  () => analysis.value?.total || candidates.value.length || 0,
);

const runAgentScoring = async () => {
  // Sequentially process each candidate to prevent overloading the local LLM
  for (let i = 0; i < candidates.value.length; i++) {
    const candidate = candidates.value[i];

    if (!candidate.agentLoading) continue; // Skip if already scored

    try {
      const response = await api.post("/screen-candidate", {
        job_profile: jobProfile.value,
        candidate: candidate,
      });
      candidate.screening = response.data.screening;
    } catch (error) {
      console.error("Agent scoring failed for", candidate.file_name, error);
      candidate.screening = {
        error: "AI Evaluation failed. Make sure Ollama is running.",
      };
    } finally {
      candidate.agentLoading = false;

      // Persist progress to sessionStorage so results remain if the user refreshes
      if (analysis.value && analysis.value.candidates[i]) {
        analysis.value.candidates[i].screening = candidate.screening;
        sessionStorage.setItem(
          "cohr_analysis_result",
          JSON.stringify(analysis.value),
        );
      }
    }
  }
};

const runSummaryAgent = async () => {
  for (let i = 0; i < candidates.value.length; i++) {
    const candidate = candidates.value[i];

    if (!candidate.summaryLoading) continue;

    try {
      const response = await api.post("/generate-summary", {
        job_description: jobDescription.value,
        resume_text: candidate.full_text || candidate.experience || "",
      });
      candidate.ai_summary = response.data.summary;
    } catch (error) {
      console.error(
        "Summary generation failed for",
        candidate.file_name,
        error,
      );
      candidate.ai_summary =
        "Failed to load AI summary. " + (error?.response?.data?.detail || "");
    } finally {
      candidate.summaryLoading = false;
      if (analysis.value && analysis.value.candidates[i]) {
        analysis.value.candidates[i].ai_summary = candidate.ai_summary;
        sessionStorage.setItem(
          "cohr_analysis_result",
          JSON.stringify(analysis.value),
        );
      }
    }
  }
};

// Load the data and begin the background agent scoring
loadAnalysis();

onMounted(() => {
  runAgentScoring();
  runSummaryAgent();
});
</script>