import { APP_NAME } from '$lib/constants';
import { type Writable, writable } from 'svelte/store';
import type { GlobalModelConfig, ModelConfig } from '$lib/apis';
import type { Banner } from '$lib/types';
import type { RoleForm } from '$lib/apis/roles';
import type { Assignment } from '$lib/apis/classes';
import type { EvaluationForm } from '$lib/apis/evaluations';

// Backend
export const WEBUI_NAME = writable(APP_NAME);
export const config: Writable<Config | undefined> = writable(undefined);
export const user: Writable<SessionUser | undefined> = writable(undefined);

// Frontend
export const MODEL_DOWNLOAD_POOL = writable({});

export const mobile = writable(false);

export const theme = writable('system');
export const chatId = writable('');

export const chats = writable([]);
export const tags = writable([]);
export const models: Writable<Model[]> = writable([]);

export const modelfiles = writable([]);
export const prompts: Writable<Prompt[]> = writable([]);
export const selectedPromptCommand: Writable<string> = writable();
export const userRoles: Writable<RoleForm[]> = writable([]);
export const classes: Writable<Class[]> = writable([]);
export const classId: Writable<number | null> = writable(null);
export const documents = writable([
	{
		collection_name: 'collection_name',
		filename: 'filename',
		name: 'name',
		title: 'title'
	},
	{
		collection_name: 'collection_name1',
		filename: 'filename1',
		name: 'name1',
		title: 'title1'
	}
]);
export const evaluations: Writable<EvaluationForm[]> = writable([]);

export const banners: Writable<Banner[]> = writable([]);

export const settings: Writable<Settings> = writable({});

export const showSidebar = writable(false);
export const showRightSidebar = writable(false);
export const showSettings = writable(false);
export const showArchivedChats = writable(false);
export const showChangelog = writable(false);

export type Model = OpenAIModel | OllamaModel;

type BaseModel = {
	id: string;
	name: string;
	info?: ModelConfig;
};

export interface OpenAIModel extends BaseModel {
	external: boolean;
	source?: string;
}

export interface OllamaModel extends BaseModel {
	details: OllamaModelDetails;
	size: number;
	description: string;
	model: string;
	modified_at: string;
	digest: string;
}

type OllamaModelDetails = {
	parent_model: string;
	format: string;
	family: string;
	families: string[] | null;
	parameter_size: string;
	quantization_level: string;
};

type Settings = {
	models?: string[];
	conversationMode?: boolean;
	speechAutoSend?: boolean;
	responseAutoPlayback?: boolean;
	audio?: AudioSettings;
	showUsername?: boolean;
	saveChatHistory?: boolean;
	notificationEnabled?: boolean;
	title?: TitleSettings;
	splitLargeDeltas?: boolean;
	chatDirection: 'LTR' | 'RTL';

	system?: string;
	requestFormat?: string;
	keepAlive?: string;
	seed?: number;
	temperature?: string;
	repeat_penalty?: string;
	top_k?: string;
	top_p?: string;
	num_ctx?: string;
	options?: ModelOptions;
};

type ModelOptions = {
	stop?: boolean;
};

export type AudioSettings = {
	STTEngine?: string;
	TTSEngine?: string;
	speaker?: string;
	model?: string;
};

type TitleSettings = {
	auto?: boolean;
	model?: string;
	modelExternal?: string;
	prompt?: string;
};

export type Prompt = {
	id: number,
	command: string;
	user_id: string;
	title: string;
	content: string;
	timestamp: number;
	is_visible: boolean;
	additional_info: string;

	image_url: string;
    evaluation_id: number | null;
    selected_model_id: string;
    evaluation_model_id: string;
    audio: AudioSettings | null;

	assigned_classes: number[];
};

export type Class = {
	id: number,
    name: string,
    instructor_id: string,
    instructor_name: string,
	image_url: string,

    assignments: Assignment[],
	assigned_students: string[]
};


type Config = {
	status: boolean;
	name: string;
	version: string;
	default_locale: string;
	default_models: string[];
	default_prompt_suggestions: PromptSuggestion[];
	features: {
		auth: boolean;
		auth_trusted_header: boolean;
		enable_signup: boolean;
		enable_web_search?: boolean;
		enable_image_generation: boolean;
		enable_admin_export: boolean;
		enable_community_sharing: boolean;
	};
};

type PromptSuggestion = {
	content: string;
	title: [string, string];
};

type SessionUser = {
	id: string;
	email: string;
	name: string;
	role: string;
	profile_image_url: string;
};
