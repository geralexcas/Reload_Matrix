<template>
  <div v-if="isTrial" class="trial-container">
    <div class="trial-info">
      <span class="trial-text">{{ daysRemaining }} días de prueba</span>
    </div>
    <div class="trial-progress-bg">
      <div class="trial-progress-fill" :style="{ width: progressPercentage + '%' }" :class="progressClass"></div>
    </div>
  </div>
</template>

<script>
import { computed, watch } from 'vue';

export default {
  name: 'TrialProgressBar',
  props: {
    company: {
      type: Object,
      required: false,
      default: null
    }
  },
  setup(props) {
    // Debugging: Watch for changes in props.company
    watch(() => props.company, (newVal) => {
      console.log('TrialProgressBar company prop changed:', newVal);
    }, { immediate: true });

    const isTrial = computed(() => {
        const val = props.company && props.company.is_trial;
        console.log('TrialProgressBar isTrial evaluated to:', val);
        return val === true;
    });
    
    const daysRemaining = computed(() => {
      if (!props.company || !props.company.created_at) return 60;
      const created = new Date(props.company.created_at);
      const now = new Date();
      const diffTime = now - created;
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      return Math.max(0, 60 - diffDays);
    });

    const progressPercentage = computed(() => {
      return Math.max(0, Math.min(100, (daysRemaining.value / 60) * 100));
    });

    const progressClass = computed(() => {
      if (daysRemaining.value <= 10) return 'trial-danger';
      if (daysRemaining.value <= 20) return 'trial-warning';
      return 'trial-success';
    });

    return { isTrial, daysRemaining, progressPercentage, progressClass };
  }
};
</script>


<style scoped>
.trial-container {
  padding: 0.5rem;
  font-size: 0.8rem;
  color: #fff;
  background-color: #2c2c44;
  border-bottom: 1px solid #444;
}
.trial-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-weight: bold;
}
.trial-progress-bg {
  height: 3px;
  background-color: #333;
  border-radius: 1.5px;
}
.trial-progress-fill {
  height: 100%;
  border-radius: 1.5px;
  transition: width 0.3s ease;
}
.trial-success { background-color: #4caf50; }
.trial-warning { background-color: #ff9800; }
.trial-danger { background-color: #f44336; }
</style>
