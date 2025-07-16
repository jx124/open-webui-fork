<script lang="ts">
	import { DatePicker } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import ChevronLeft from '../icons/ChevronLeft.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import CalendarBlank from '../icons/CalendarBlank.svelte';
	import { CalendarDateTime, parseDate } from '@internationalized/date';
	import { mobile } from '$lib/stores';

	let selectedDate = null;
	
	export let selectedDateTime;
	export let placeholder: string | null;
	let parsedPlaceholder = placeholder ? parseDate(placeholder.split('T')[0]) : undefined;
	let selectedTime = placeholder ? placeholder.split('T')[1].slice(0, 5) : "23:59";

	$: if ((selectedDate || parsedPlaceholder) && selectedTime) {
		selectedDateTime = new CalendarDateTime(
			selectedDate?.year ?? parsedPlaceholder?.year,
			selectedDate?.month ?? parsedPlaceholder?.month,
			selectedDate?.day ?? parsedPlaceholder?.day,
			parseInt(selectedTime.split(":")[0]),
			parseInt(selectedTime.split(":")[1]),
			59
		).toString();
	}
</script>

<DatePicker.Root weekdayFormat="short" fixedWeeks={true} value={parsedPlaceholder}>
	<div class="flex flex-row gap-1.5 mt-2">
		<div class="flex w-full max-w-[180px] flex-col gap-1.5">
			<DatePicker.Label class="block select-none text-xs font-medium">Select Date:</DatePicker.Label>
			<DatePicker.Input
				let:segments
				class="flex h-input w-full max-w-[180px] bg-transparent border dark:border-gray-600 outline-none rounded-lg 
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
				sideOffset={12}
				transition={flyAndScale}
				transitionConfig={{ duration: 150, y: -8 }}
				side={$mobile ? 'bottom' : 'right'}
				class="z-[70]"
			>
				<DatePicker.Calendar
					class="rounded-[15px] bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-300/30 dark:border-gray-700/50 z-[70] p-[22px] shadow-popover"
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
														on:click={() => (selectedDate = date)}
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
		<div class="flex w-full h-full max-w-[100px] min-h-[75px] flex-col gap-1.5 ml-12">
			<div class="block select-none text-xs font-medium">Select Time:</div>
			<input
				class="flex h-full min-h-[50px] w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg
                select-none items-center px-2 py-2 text-sm tracking-[0.01em] text-gray-700 dark:text-gray-100 focus-visible:ring-0 focus-visible:ring-offset-0"
				type="time"
				bind:value={selectedTime}
			/>

		</div>
	</div></DatePicker.Root
>
