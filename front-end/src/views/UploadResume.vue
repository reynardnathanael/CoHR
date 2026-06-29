<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="card col-span-12 xl:col-span-7">
            <div class="px-4 mt-3 w-full rounded-2xl bg-indigo-900">
                <p class="text-white text-lg pt-3 font-semibold">Upload a CV or Resume</p>
                <FileUpload @select="updateFileCount" @remove="updateFileCount" @clear="updateFileCount" :showUploadButton="false" ref="fileUpload" name="files" :multiple="true" accept="application/pdf" :auto="false" style="border: 0;" class="bg-indigo-900">
                    <template #empty>
                        <div class="flex justify-center items-center space-x-4 border-2 py-4 border-dashed rounded-2xl" style="border-color: #1C1C1C;">
                            <!-- <i class="pi pi-cloud-upload !text-4xl" /> -->
                            <div class="flex flex-col items-center">
                                <img src="../assets/img/cloud.png" alt="" class="h-20 w-20">
                                <p class="text-lg font-semibold">Drag and drop your file here</p>
                            </div>
                        </div> 
                    </template>
                    <template #content="{ files, removeFileCallback }">
                        <div v-if="files.length > 0" class="flex flex-col gap-4 mt-4">
                            <div v-for="(file, index) of files" :key="file.name + file.type + file.size" class="p-4 rounded-xl flex items-center gap-4 bg-indigo-50 border border-indigo-700">
                                <i class="pi pi-file-pdf text-9xl text-red-400" style="font-size: 2rem;"></i>
                                <div class="flex flex-col flex-1 overflow-hidden">
                                    <span class="font-semibold text-ellipsis whitespace-nowrap overflow-hidden text-indigo-800">{{ file.name }}</span>
                                    <span class="text-sm text-indigo-800">{{ formatSize(file.size) }}</span>
                                </div>
                                <Button icon="pi pi-times" @click="removeFileCallback(index)" variant="text" rounded severity="danger" class="hover:bg-indigo-700" />
                            </div>
                        </div>
                    </template>
                </FileUpload>
                <p class="text-white py-3 text-sm">Upload one or more PDF resumes</p>
            </div>
            <div class="my-8 flex justify-center">
                <Select v-model="selectedRole" :options="roles" filter optionLabel="name" placeholder="Select job position" class="w-full">
                    <template #value="slotProps">
                        <div v-if="slotProps.value" class="flex items-center">
                        <div class="text-lg">{{ slotProps.value.name }}</div>
                        </div>
                    <span v-else class="text-lg">
                            {{ slotProps.placeholder }}
                        </span>
                    </template>
                    <template #option="slotProps">
                        <div class="flex items-center">
                        <div class="text-lg">{{ slotProps.option.name }}</div>
                        </div>
                    </template>
                </Select>
            </div>
            <div class="flex flex-col gap-1">
                <label for="description" class="text-lg font-medium ">Job Description</label>
                <Textarea class="text-justify" id="description" v-model="jobDescription" rows="5" fluid autoResize readonly />
            </div>
            <div class="flex flex-col items-center mt-10 pb-5">
                <Button :loading="loading" class="w-40 mb-2 !bg-indigo-200 !text-black !border-indigo-900" type="button" label="Submit" icon="pi pi-upload" iconPos="right" @click="createPostFile" style="border-radius: 16px;"></Button>
                <p v-if="statusMessage" class="text-sm text-indigo-700 font-medium animate-pulse">{{ statusMessage }}</p>
            </div>
        </div>

        <!-- Right column: Screening History -->
        <div class="card col-span-12 xl:col-span-5">
            <div class="flex items-center justify-between">
                <h4 class="text-xl font-semibold text-slate-900">Screening History</h4>
                <Badge v-if="history.length" :value="history.length" severity="info" />
            </div>

            <div v-if="historyLoading" class="space-y-4">
                <div v-for="i in 3" :key="i" class="flex items-center gap-3">
                    <Skeleton shape="circle" size="2.5rem" />
                    <div class="flex-1">
                        <Skeleton width="60%" height="1rem" class="mb-2" />
                        <Skeleton width="40%" height="0.75rem" />
                    </div>
                </div>
            </div>

            <div v-else-if="selectedRole && history.length > 0" class="overflow-y-auto max-h-[600px] pr-2">
                <ul class="space-y-3">
                    <li v-for="(item, index) in history" :key="index" class="flex items-center justify-between gap-4 p-3 rounded-xl border border-slate-100 bg-slate-50 hover:bg-slate-100 transition-colors">
                        <div class="flex items-center gap-3 overflow-hidden">
                            <div class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold text-sm flex items-center justify-center">
                                {{ index + 1 }}
                            </div>
                            <div class="overflow-hidden">
                                <p class="font-semibold text-slate-800 truncate" :title="item.name">{{ item.name }}</p>
                                <Badge :value="item.fit_category" :severity="getBadgeSeverity(item.fit_category)" class="mt-1" />
                            </div>
                        </div>
                        <div class="text-right flex-shrink-0">
                            <p class="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Match</p>
                            <p class="text-lg font-bold text-indigo-900">{{ item.fit_score.toFixed(1) }}%</p>
                        </div>
                    </li>
                </ul>
            </div>

            <div v-else-if="selectedRole && history.length === 0" class="text-center py-12 text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                <i class="pi pi-inbox text-6xl text-slate-300 mb-4"></i>
                <p class="text-xl font-medium">No candidates found for this role yet.</p>
                <p class="text-base mt-1">Upload resumes to get started!</p>
            </div>

            <div v-else class="text-center py-12 text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                <i class="pi pi-search text-6xl text-slate-300 mb-4"></i>
                <p class="text-xl font-medium">Select a job position</p>
                <p class="text-base mt-1">to view its screening history.</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { api } from "../helpers/axios";
import { useRouter } from "vue-router";
import Badge from 'primevue/badge';
import Skeleton from 'primevue/skeleton';

const fileUpload = ref();
const router = useRouter();
const selectedRole = ref();
const jobDescription = ref("");
const loading = ref(false);
const statusMessage = ref("");

const history = ref([]);
const historyLoading = ref(false);

const defaultJobDescription = jobDescription.value;
const formatRoleDescription = (description) => {
    if (!description || typeof description !== 'string') {
        return '';
    }

    return description
        .split(';')
        .map((item) => item.trim())
        .filter(Boolean)
        .map((item) => `• ${item}`)
        .join('\n');
};

const roleDescriptions = {
    'Business Analyst': formatRoleDescription("Master's degree or equivalent practical experience; Certified Supply Chain Professional (CSCP) from APICS; 5 years of experience designing, configuring, and testing Enterprise Resource Planning (ERP) Logistic and Warehouse Management Systems (SAP, EWM); 5 years of experience in either Supply Chain Logistics, the Transportation Industry, or Data Center Environment and Safety; 5 years of experience translating business problems into research questions and translating research findings and insights into marketing recommendations; 5 years of experience designing, scoping, executing, and delivering research and analysis projects; Experience leading solution architecture and systems integrations; Experience in management consulting focus on marketing measurement or quantitative disciplines; Experience managing research and measurement agencies; Experience influencing executive leadership with cohesive narratives built on a mix of qualitative and quantitative data; Proficiency in working with database technologies, including both standalone and cloud-based databases, for data extraction and quantitative data manipulation, with experience in SQL, BI, and agentic tools (e.g., Looker, Gemini for insights); Familiarity with scripting languages (Python) and data science techniques; Proficiency in identifying, assessing, estimating, and resolving complex business challenges, particularly those that involve evaluating variable factors, including security considerations; Ability to solve problems in changing, and ambiguous business environments through data intuition and business acumen; Knowledge of logistics and execution processes with excellent investigative skills; Ability to effectively communicate findings, approaches, and recommendations to a wide range of technical and non-technical audiences"),
    'Data Scientist': formatRoleDescription("Master's degree in Statistics, Data Science, Mathematics, Physics, Economics, Operations Research, Engineering, or a related quantitative field; 10 years of work experience using analytics to solve product or business problems, coding (e.g., Python, R, SQL), querying databases or statistical analysis, or 8 years of work experience with a PhD degree; Familiarity with modern Machine Learning and Large Language Model (LLM) techniques; Ability to commit to knowledge and learning, respect for science, tolerance for ambiguity, and interest in practical application of science to business; Excellent collaboration skills, with the ability to collaborate cross-functionally and work effectively with Data Scientist (DS), User Experience Researcher (UXR), product and engineering partners"),
    'DevOps Engineer': formatRoleDescription("Master’s degree or PhD in Engineering, Computer Science, or a related technical field; 8 years of experience programming in C++; 5 years of experience testing and launching software products; 5 years of experience building and developing large-scale infrastructure, distributed systems, or networks, with deep expertise in compute technologies, storage, or hardware architecture; 3 years of experience in software design and architecture, including a proven track record of building cloud architecture in a production environment while balancing short-term and long-term needs; 2 years of experience in a technical leadership role, guiding and mentoring a team of cloud/DevOps engineers, with the ability to establish and enforce engineering best practices, coding standards, and architectural patterns; Ability to take ownership of large, ambiguous technical projects, break them down into manageable tasks, and drive them to successful completion"),
    'Digital Media Expert': formatRoleDescription("Bachelor’s degree or equivalent practical experience; 6 years of experience in Product Marketing, Social Media Strategy, or Digital Advertising; Experience turning technical product concepts into social content; Understanding of social platforms, including social media platforms and YouTube, with a deep knowledge of targeting, bidding strategies, and performance measurement; Ability to develop and execute successful social strategies that have a direct and measurable impact on the business; Ability to grow in a fast-paced environment and pivot strategies based on breaking news or industry shifts; Excellent analytical skills with the ability to define and track key business metrics, analyze data, and translate insights into actionable strategies"),
    'Human Resources': formatRoleDescription("Master's or MBA degree, or equivalent practical experience; 12 years of experience as an HR business partner or HR generalist supporting leaders at global companies; Experience in organizational effectiveness, including workforce planning and organizational design; Expertise in talent management, total rewards, employee relations, and HR data analytics; Demonstrated ability to work within constraints as well as challenge the status quo; Effective communicator with the ability to build relationships with senior leaders and a complex set of stakeholders to drive organizational change; Demonstrated analytical and problem solving skills, including ability to analyze data, understand trends and develop recommendations for actions based on the analysis; Comfortable with ambiguity and being a part of deeply complex strategy discussions"),
};

const roles = ref([
    { name: 'Business Analyst' },
    { name: 'Data Scientist' },
    { name: 'DevOps Engineer' },
    { name: 'Digital Media Expert' },
    { name: 'Human Resources' },
]);

const fetchHistory = async (roleName) => {
    if (!roleName) {
        history.value = [];
        return;
    }
    historyLoading.value = true;
    try {
        const response = await api.get(`/history/${encodeURIComponent(roleName)}`);
        history.value = response.data;
    } catch (error) {
        console.error(`Failed to fetch history for ${roleName}:`, error);
        history.value = [];
    } finally {
        historyLoading.value = false;
    }
};

const getBadgeSeverity = (category) => {
    const lower = category?.toLowerCase() || '';
    if (lower.includes('strong')) return 'success';
    if (lower.includes('potential')) return 'warning';
    if (lower.includes('weak')) return 'danger';
    return 'info';
};

watch(selectedRole, (role) => {
    const roleName = role?.name;
    jobDescription.value = roleName && roleDescriptions[roleName]
        ? roleDescriptions[roleName]
        : defaultJobDescription;
        
    fetchHistory(roleName);
});

const updateFileCount = () => {
    const files = fileUpload.value?.files || [];
    statusMessage.value = files.length > 0
        ? `${files.length} file(s) ready for analysis.`
        : '';
};

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const normalizeTextArray = (value) => {
    if (Array.isArray(value)) {
        return value.filter(Boolean);
    }

    if (typeof value === 'string' && value.trim()) {
        return [value.trim()];
    }

    return [];
};

const formatLocation = (value) => {
    if (!value) {
        return '';
    }

    if (typeof value === 'string') {
        return value.trim();
    }

    if (Array.isArray(value)) {
        return value
            .map((entry) => formatLocation(entry))
            .filter(Boolean)
            .join(', ');
    }

    if (typeof value === 'object') {
        const parts = [
            value.location,
            value.city,
            value.state,
            value.region,
            value.country,
            value.name,
        ].filter((part) => typeof part === 'string' && part.trim());

        return parts.join(', ');
    }

    return '';
};

const normalizeCandidate = (candidate) => ({
    ...candidate,
    location: formatLocation(
        candidate?.location ||
        candidate?.extracted_location ||
        candidate?.contact?.location ||
        candidate?.contact?.city ||
        candidate?.city ||
        candidate?.country
    ),
    matched_skills: normalizeTextArray(candidate?.matched_skills),
    extracted_skills: normalizeTextArray(candidate?.extracted_skills),
});

const normalizeAnalysisResult = (payload) => ({
    ...payload,
    candidates: Array.isArray(payload?.candidates)
        ? payload.candidates.map(normalizeCandidate)
        : [],
});

const createPostFile = async () => {
    if (!fileUpload.value || fileUpload.value.files.length === 0) {
        alert("Please select at least one PDF file first.");
        return;
    }

    const formData = new FormData();
    const files = Array.from(fileUpload.value.files);

    files.forEach((file) => {
        formData.append('files', file);
    });
    formData.append('job_title', selectedRole.value?.name || 'Uploaded Job');
    formData.append('job_description', jobDescription.value);

    loading.value = true;
    statusMessage.value = 'Extracting resume data...';

    try {
        const response = await api.post('/analyze-fast', formData);
        const normalizedResult = normalizeAnalysisResult(response.data);
        normalizedResult.job_description = jobDescription.value;

        sessionStorage.setItem('cohr_analysis_result', JSON.stringify(normalizedResult));
        statusMessage.value = `Extraction complete. Proceeding to score ${normalizedResult.total} candidate(s)...`;
        await router.push('/result');
    } catch (error) {
        console.error("Error uploading resumes:", error);
        if (!error?.response) {
            statusMessage.value = 'Could not reach the backend at http://localhost:8080. Start the FastAPI server, then try again.';
        } else {
            statusMessage.value = error?.response?.data?.detail || 'Something went wrong while analyzing resumes.';
        }
    } finally {
        loading.value = false;
    }
};
</script>
