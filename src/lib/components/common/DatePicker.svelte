<script lang="ts">
	import { DatePicker } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import ChevronLeft from '../icons/ChevronLeft.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import CalendarBlank from '../icons/CalendarBlank.svelte';
	import { CalendarDateTime, parseDate } from '@internationalized/date';
	
    export let header = "";
	
	let selectedDate;

	export let selectedDateTime;
	export let placeholder: string | null;
	let parsedPlaceholder = placeholder ? parseDate(placeholder.split("T")[0]) : undefined;
	
	$: if (selectedDate) {
		selectedDateTime = new CalendarDateTime(selectedDate?.year, selectedDate?.month, selectedDate?.day, 23, 59, 59).toString();
	} 
    
</script>

<DatePicker.Root weekdayFormat="short" fixedWeeks={true} value={parsedPlaceholder}>
	<div class="flex w-full max-w-[232px] flex-col gap-1.5">
		<DatePicker.Label class="block select-none text-sm font-medium">{header}</DatePicker.Label>
		<DatePicker.Input
			let:segments
			class="flex h-input w-full max-w-[232px] bg-transparent border dark:border-gray-600 outline-none rounded-lg 
                select-none items-center px-2 py-2 text-sm tracking-[0.01em] text-gray-700 dark:text-gray-100"
		>
			{#each segments as { part, value }}
				<div class="inline-block select-none">
					{#if part === 'literal'}
						<DatePicker.Segment {part} class="p-1 text-gray-500 dark:text-gray-400">
							{value}
						</DatePicker.Segment>
					{:else}
						<DatePicker.Segment
							{part}
							class="rounded-md px-1 py-1 dark:hover:bg-gray-800 hover:bg-gray-200 dark:focus:bg-gray-800 focus:bg-gray-200 focus:text-gray-700 focus:dark:text-gray-100 
                            focus-visible:ring-0 focus-visible:ring-offset-0 aria-[valuetext=Empty]:text-gray-500 aria-[valuetext=Empty]:dark:text-gray-400"
						>
							{value}
						</DatePicker.Segment>
					{/if}
				</div>
			{/each}
			<DatePicker.Trigger
				class="ml-auto inline-flex rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition size-8 items-center justify-center text-gray-700/60 dark:text-gray-100/60"
			>
				<CalendarBlank />
			</DatePicker.Trigger>
		</DatePicker.Input>
		<DatePicker.Content
			sideOffset={6}
			transition={flyAndScale}
			transitionConfig={{ duration: 150, y: -8 }}
			class="z-50"
		>
			<DatePicker.Calendar
				class="rounded-[15px] bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-300/30 dark:border-gray-700/50 z-50 p-[22px] shadow-popover"
				let:months
				let:weekdays
			>
				<DatePicker.Header class="flex items-center justify-between">
					<DatePicker.PrevButton
						class="inline-flex size-10 items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition active:scale-98"
					>
						<ChevronLeft />
					</DatePicker.PrevButton>
					<DatePicker.Heading class="text-[15px] font-medium" />
					<DatePicker.NextButton
						class="inline-flex size-10 items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition active:scale-98"
					>
						<ChevronRight />
					</DatePicker.NextButton>
				</DatePicker.Header>
				<div class="flex flex-col space-y-4 pt-4 sm:flex-row sm:space-x-4 sm:space-y-0">
					{#each months as month}
						<DatePicker.Grid class="w-full border-collapse select-none space-y-1">
							<DatePicker.GridHead>
								<DatePicker.GridRow class="mb-1 flex w-full justify-between">
									{#each weekdays as day}
										<DatePicker.HeadCell
											class="w-10 rounded-md text-xs font-normal text-gray-400 dark:text-gray-500"
										>
											<div>{day.slice(0, 2)}</div>
										</DatePicker.HeadCell>
									{/each}
								</DatePicker.GridRow>
							</DatePicker.GridHead>
							<DatePicker.GridBody>
								{#each month.weeks as weekDates}
									<DatePicker.GridRow class="flex w-full">
										{#each weekDates as date}
											<DatePicker.Cell {date} class="relative size-10 !p-0 text-center text-sm">
												<DatePicker.Day
                                                    on:click={() => selectedDate = date}
													{date}
													month={month.value}
													class="group relative inline-flex size-10 items-center justify-center whitespace-nowrap rounded-lg 
                                                            border border-transparent bg-transparent p-0 text-sm font-normal text-gray-700 dark:text-gray-100 transition-all 
                                                            hover:bg-gray-100 dark:hover:bg-gray-800 data-[disabled]:pointer-events-none data-[outside-month]:pointer-events-none 
                                                            data-[selected]:bg-gray-100 data-[selected]:dark:bg-gray-800 data-[selected]:font-medium data-[selected]:text-background 
                                                            data-[disabled]:text-gray-400 data-[disabled]:dark:text-gray-500 
                                                            data-[unavailable]:text-gray-500 data-[unavailable]:dark:text-gray-400 data-[unavailable]:line-through"
												>
													<div
														class="absolute top-[5px] hidden size-1 rounded-full bg-gray-800 dark:bg-gray-200 transition-all group-data-[today]:block group-data-[selected]:bg-background"
													/>
													{date.day}
												</DatePicker.Day>
											</DatePicker.Cell>
										{/each}
									</DatePicker.GridRow>
								{/each}
							</DatePicker.GridBody>
						</DatePicker.Grid>
					{/each}
				</div>
			</DatePicker.Calendar>
		</DatePicker.Content>
	</div>
</DatePicker.Root>
